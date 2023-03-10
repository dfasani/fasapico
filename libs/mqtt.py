

import json
import sys
import utime

import usocket as socket
import ustruct as struct
from ubinascii import hexlify


class MQTTException(Exception):
    pass


class MQTTClientSimple:
    def __init__(
        self,
        client_id,
        server,
        port=0,
        user=None,
        password=None,
        keepalive=0,
        ssl=False,
        ssl_params={},
    ):
        if port == 0:
            port = 8883 if ssl else 1883
        self.client_id = client_id
        self.sock = None
        self.server = server
        self.port = port
        self.ssl = ssl
        self.ssl_params = ssl_params
        self.pid = 0
        self.cb = None
        self.user = user
        self.pswd = password
        self.keepalive = keepalive
        self.lw_topic = None
        self.lw_msg = None
        self.lw_qos = 0
        self.lw_retain = False

    def _send_str(self, s):
        self.sock.write(struct.pack("!H", len(s)))
        self.sock.write(s)

    def _recv_len(self):
        n = 0
        sh = 0
        while 1:
            b = self.sock.read(1)[0]
            n |= (b & 0x7F) << sh
            if not b & 0x80:
                return n
            sh += 7

    def set_callback(self, f):
        self.cb = f

    def set_last_will(self, topic, msg, retain=False, qos=0):
        assert 0 <= qos <= 2
        assert topic
        self.lw_topic = topic
        self.lw_msg = msg
        self.lw_qos = qos
        self.lw_retain = retain

    def connect(self, clean_session=True):
        self.sock = socket.socket()
        addr = socket.getaddrinfo(self.server, self.port)[0][-1]
        self.sock.connect(addr)
        if self.ssl:
            import ussl

            self.sock = ussl.wrap_socket(self.sock, **self.ssl_params)
        premsg = bytearray(b"\x10\0\0\0\0\0")
        msg = bytearray(b"\x04MQTT\x04\x02\0\0")

        sz = 10 + 2 + len(self.client_id)
        msg[6] = clean_session << 1
        if self.user is not None:
            sz += 2 + len(self.user) + 2 + len(self.pswd)
            msg[6] |= 0xC0
        if self.keepalive:
            assert self.keepalive < 65536
            msg[7] |= self.keepalive >> 8
            msg[8] |= self.keepalive & 0x00FF
        if self.lw_topic:
            sz += 2 + len(self.lw_topic) + 2 + len(self.lw_msg)
            msg[6] |= 0x4 | (self.lw_qos & 0x1) << 3 | (self.lw_qos & 0x2) << 3
            msg[6] |= self.lw_retain << 5

        i = 1
        while sz > 0x7F:
            premsg[i] = (sz & 0x7F) | 0x80
            sz >>= 7
            i += 1
        premsg[i] = sz

        self.sock.write(premsg, i + 2)
        self.sock.write(msg)
        # print(hex(len(msg)), hexlify(msg, ":"))
        self._send_str(self.client_id)
        if self.lw_topic:
            self._send_str(self.lw_topic)
            self._send_str(self.lw_msg)
        if self.user is not None:
            self._send_str(self.user)
            self._send_str(self.pswd)
        resp = self.sock.read(4)
        assert resp[0] == 0x20 and resp[1] == 0x02
        if resp[3] != 0:
            raise MQTTException(resp[3])
        return resp[2] & 1

    def disconnect(self):
        self.sock.write(b"\xe0\0")
        self.sock.close()

    def ping(self):
        self.sock.write(b"\xc0\0")

    def publish(self, topic, msg, retain=False, qos=0):
        pkt = bytearray(b"\x30\0\0\0")
        pkt[0] |= qos << 1 | retain
        sz = 2 + len(topic) + len(msg)
        if qos > 0:
            sz += 2
        assert sz < 2097152
        i = 1
        while sz > 0x7F:
            pkt[i] = (sz & 0x7F) | 0x80
            sz >>= 7
            i += 1
        pkt[i] = sz
        # print(hex(len(pkt)), hexlify(pkt, ":"))
        self.sock.write(pkt, i + 1)
        self._send_str(topic)
        if qos > 0:
            self.pid += 1
            pid = self.pid
            struct.pack_into("!H", pkt, 0, pid)
            self.sock.write(pkt, 2)
        self.sock.write(msg)
        if qos == 1:
            while 1:
                op = self.wait_msg()
                if op == 0x40:
                    sz = self.sock.read(1)
                    assert sz == b"\x02"
                    rcv_pid = self.sock.read(2)
                    rcv_pid = rcv_pid[0] << 8 | rcv_pid[1]
                    if pid == rcv_pid:
                        return
        elif qos == 2:
            assert 0

    def subscribe(self, topic, qos=0):
        assert self.cb is not None, "Subscribe callback is not set"
        pkt = bytearray(b"\x82\0\0\0")
        self.pid += 1
        struct.pack_into("!BH", pkt, 1, 2 + 2 + len(topic) + 1, self.pid)
        # print(hex(len(pkt)), hexlify(pkt, ":"))
        self.sock.write(pkt)
        self._send_str(topic)
        self.sock.write(qos.to_bytes(1, "little"))
        while 1:
            op = self.wait_msg()
            if op == 0x90:
                resp = self.sock.read(4)
                # print(resp)
                assert resp[1] == pkt[2] and resp[2] == pkt[3]
                if resp[3] == 0x80:
                    raise MQTTException(resp[3])
                return

    # Wait for a single incoming MQTT message and process it.
    # Subscribed messages are delivered to a callback previously
    # set by .set_callback() method. Other (internal) MQTT
    # messages processed internally.
    def wait_msg(self):
        res = self.sock.read(1)
        self.sock.setblocking(True)
        if res is None:
            return None
        if res == b"":
            raise OSError(-1)
        if res == b"\xd0":  # PINGRESP
            sz = self.sock.read(1)[0]
            assert sz == 0
            return None
        op = res[0]
        if op & 0xF0 != 0x30:
            return op
        sz = self._recv_len()
        topic_len = self.sock.read(2)
        topic_len = (topic_len[0] << 8) | topic_len[1]
        topic = self.sock.read(topic_len)
        sz -= topic_len + 2
        if op & 6:
            pid = self.sock.read(2)
            pid = pid[0] << 8 | pid[1]
            sz -= 2
        msg = self.sock.read(sz)
        self.cb(topic, msg)
        if op & 6 == 2:
            pkt = bytearray(b"\x40\x02\0\0")
            struct.pack_into("!H", pkt, 2, pid)
            self.sock.write(pkt)
        elif op & 6 == 4:
            assert 0
        return op

    # Checks whether a pending message from server is available.
    # If not, returns immediately with None. Otherwise, does
    # the same processing as wait_msg.
    def check_msg(self):
        self.sock.setblocking(False)
        return self.wait_msg()


class MQTTClient(MQTTClientSimple):
    DELAY = 2
    DEBUG = False

    def delay(self, i):
        utime.sleep(self.DELAY)

    def log(self, in_reconnect, e):
        if self.DEBUG:
            if in_reconnect:
                print("mqtt reconnect: %r" % e)
            else:
                print("mqtt: %r" % e)

    def reconnect(self):
        i = 0
        while 1:
            try:
                return super().connect(False)
            except OSError as e:
                self.log(True, e)
                i += 1
                self.delay(i)

    def publish(self, topic, msg, retain=False, qos=0):
        while 1:
            try:
                return super().publish(topic, msg, retain, qos)
            except OSError as e:
                self.log(False, e)
            self.reconnect()

    def wait_msg(self):
        while 1:
            try:
                return super().wait_msg()
            except OSError as e:
                self.log(False, e)
            self.reconnect()

    def check_msg(self, attempts=2):
        while attempts:
            self.sock.setblocking(False)
            try:
                return super().wait_msg()
            except OSError as e:
                self.log(False, e)
            self.reconnect()
            attempts -= 1

RPC_RESPONSE_TOPIC = 'v1/devices/me/rpc/response/'
RPC_REQUEST_TOPIC = 'v1/devices/me/rpc/request/'
ATTRIBUTES_TOPIC = 'v1/devices/me/attributes'
ATTRIBUTES_TOPIC_REQUEST = 'v1/devices/me/attributes/request/'
ATTRIBUTES_TOPIC_RESPONSE = 'v1/devices/me/attributes/response/'
TELEMETRY_TOPIC = 'v1/devices/me/telemetry'
CLAIMING_TOPIC = 'v1/devices/me/claim'
PROVISION_TOPIC_REQUEST = '/provision/request'
PROVISION_TOPIC_RESPONSE = '/provision/response'


class TBQoSException(Exception):
    pass


class TBAuthException(Exception):
    pass


def validate_qos(qos):
    if qos not in (0, 1):
        raise TBQoSException('Quality of service (qos) value must be 0 or 1')


class TBDeviceMqttClient:

    DEBUG = False

    def __init__(self, host, port=1883, access_token=None, basic_auth=None,
                 keepalive=0, ssl_params=None, qos=0):
        validate_qos(qos)

        # validate authentication
        if access_token and basic_auth:
            raise TBAuthException('Only one auth method must be provided')
        elif access_token:
            user = access_token
            password = client_id = ''
        elif basic_auth:
            valid_keys = ('user', 'password', 'client_id')
            if not all(k in valid_keys for k in basic_auth.keys()):
                raise TBAuthException('valid keys are {}'.format(valid_keys))
            elif basic_auth.get('password') and not basic_auth.get('user'):
                raise TBAuthException('user must be provided')
            elif not basic_auth.get('user') and not basic_auth.get('client_id'):
                raise TBAuthException('client_id or user must be provided')
            user = basic_auth.get('user', '')
            password = basic_auth.get('password', '')
            client_id = basic_auth.get('client_id', '')
        else:
            raise TBAuthException('At least one auth method must be provided')

        ssl_params = ssl_params if ssl_params else {}
        self._client = MQTTClient(client_id, host, port=port, user=user,
                                  password=password, keepalive=keepalive,
                                  ssl=bool(ssl_params), ssl_params=ssl_params)

        self._qos = qos
        self._is_connected = False
        self._attr_request_dict = {}
        self._device_on_server_side_rpc_response = None
        self._device_max_sub_id = 0
        self._device_client_rpc_number = 0
        self._device_sub_dict = {}
        self._device_client_rpc_dict = {}
        self._attr_request_number = 0
        self._client.set_callback(self._on_message)

    def is_connected(self):
        return self._is_connected

    def connect(self):
        if self._is_connected:
            return 0

        ret = self._client.connect()
        if ret == 0:
            self._log('Connected to ThingsBoard')
            self._is_connected = True
            self._log('Subscribing to attributes and RPC topics')
            self._client.subscribe(ATTRIBUTES_TOPIC, qos=self._qos)
            self._client.subscribe(ATTRIBUTES_TOPIC + '/response/+',
                                   qos=self._qos)
            self._client.subscribe(RPC_REQUEST_TOPIC + '+', qos=self._qos)
            self._client.subscribe(RPC_RESPONSE_TOPIC + '+', qos=self._qos)
        return ret

    def reconnect(self):
        self._log('Reconnecting to ThingsBoard')
        return self._client.reconnect()

    def disconnect(self):
        if self._is_connected:
            self._log('Disconnecting from ThingsBoard')
            self._client.disconnect()
            self._is_connected = False

    def wait_msg(self):
        return self._client.wait_msg()

    def check_msg(self):
        return self._client.check_msg()

    def claim(self, secret_key, duration=30000):
        claiming_request = {
            'secretKey': secret_key,
            'durationMs': duration
        }
        self._client.publish(CLAIMING_TOPIC, json.dumps(
            claiming_request), qos=self._qos)

    def send_rpc_reply(self, req_id, resp, qos=0):
        validate_qos(qos)
        self._client.publish(RPC_RESPONSE_TOPIC + req_id, resp, qos=qos)

    def send_rpc_call(self, method, params, callback):
        self._device_client_rpc_number += 1
        self._device_client_rpc_dict.update(
            {self._device_client_rpc_number: callback})
        rpc_request_id = self._device_client_rpc_number
        payload = {'method': method, 'params': params}
        self._client.publish(RPC_REQUEST_TOPIC + str(rpc_request_id),
                             json.dumps(payload),
                             qos=self._qos)

    def set_server_side_rpc_request_handler(self, handler):
        # handler signature is callback(req_id, method, params)
        self._device_on_server_side_rpc_response = handler

    def publish_data(self, topic, data, qos=0):
        validate_qos(qos)
        self._client.publish(topic, json.dumps(data), qos=qos)

    def send_telemetry(self, telemetry, qos=0):
        if not isinstance(telemetry, list):
            telemetry = [telemetry]
        return self.publish_data(TELEMETRY_TOPIC, telemetry, qos=qos)

    def send_attributes(self, attributes, qos=0):
        # attributes is a string or a list of strings
        return self.publish_data(ATTRIBUTES_TOPIC, attributes, qos=qos)

    def unsubscribe_from_attribute(self, subscription_id):
        for attribute in self._device_sub_dict:
            if self._device_sub_dict[attribute].get(subscription_id):
                del self._device_sub_dict[attribute][subscription_id]
                self._log('Unsubscribed from %s, subscription id %i',
                          attribute, subscription_id)
        if subscription_id == '*':
            self._device_sub_dict = {}
        self._device_sub_dict = dict(
            (k, v) for k, v in self._device_sub_dict.items() if v)

    def subscribe_to_all_attributes(self, callback):
        # callback signature is callback(attributes)
        return self.subscribe_to_attribute('*', callback)

    def subscribe_to_attribute(self, key, callback):
        # callback signature is callback(attributes)
        self._device_max_sub_id += 1
        if key not in self._device_sub_dict:
            self._device_sub_dict.update(
                {key: {self._device_max_sub_id: callback}})
        else:
            self._device_sub_dict[key].update(
                {self._device_max_sub_id: callback})
        self._log('Subscribed to %s with id %i', key, self._device_max_sub_id)
        return self._device_max_sub_id

    def request_attributes(self, client_keys=None, shared_keys=None,
                           callback=None):
        # callback signature is callback(resp_id, attributes)
        if client_keys is None and shared_keys is None:
            self._log('There are no keys to request')
            return False

        msg = {}
        if client_keys:
            msg.update({'clientKeys': ','.join(client_keys)})
        if shared_keys:
            msg.update({'sharedKeys': ','.join(shared_keys)})

        req_id = self._add_attr_request_callback(callback)
        self._client.publish(ATTRIBUTES_TOPIC_REQUEST + str(req_id),
                             json.dumps(msg),
                             qos=self._qos)
        return True

    def _add_attr_request_callback(self, callback):
        self._attr_request_number += 1
        self._attr_request_dict.update({self._attr_request_number: callback})
        return self._attr_request_number

    def _on_message(self, topic, msg):
        topic = topic.decode('utf-8')
        payload = json.loads(msg.decode('utf-8'))
        self._log('Rx on {}: {}'.format(topic, payload))
        self._on_decoded_message(topic, payload)

    def _on_decoded_message(self, topic, payload):
        if topic.startswith(RPC_REQUEST_TOPIC):
            req_id = topic[len(RPC_REQUEST_TOPIC):]
            if self._device_on_server_side_rpc_response:
                method = payload.get('method')
                params = payload.get('params')
                self._device_on_server_side_rpc_response(req_id, method,
                                                         params)
        elif topic.startswith(RPC_RESPONSE_TOPIC):
            resp_id = int(topic[len(RPC_RESPONSE_TOPIC):])
            callback = self._device_client_rpc_dict.pop(resp_id)
            if callback:
                callback(resp_id, payload)
        elif topic == ATTRIBUTES_TOPIC:
            callbacks = []
            # callbacks for everything
            if self._device_sub_dict.get('*'):
                for subscription_id in self._device_sub_dict['*']:
                    callbacks.append(
                        self._device_sub_dict['*'][subscription_id])
            # specific callback, iterate through message
            for key in payload.keys():
                # find key in our dict
                if self._device_sub_dict.get(key):
                    for subscription in self._device_sub_dict[key]:
                        callbacks.append(
                            self._device_sub_dict[key][subscription])
            for cb in callbacks:
                cb(payload)
        elif topic.startswith(ATTRIBUTES_TOPIC_RESPONSE):
            resp_id = int(topic[len(ATTRIBUTES_TOPIC + '/response/'):])
            callback = self._attr_request_dict.pop(resp_id)
            if callback:
                callback(payload)

    def _log(self, msg, *args):
        if self.DEBUG:
            stream = sys.stderr.write('%s:%s:' % (self.__name__))
            if not args:
                print(msg, file=stream)
            else:
                print(msg % args, file=stream)


