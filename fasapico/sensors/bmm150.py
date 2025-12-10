# -*- coding: utf-8 -*

import utime
from machine import I2C, Pin, SoftI2C
import math


class trim_register:
  def __init__(self):
    self.dig_x1   = 0
    self.dig_y1   = 0
    self.dig_x2   = 0
    self.dig_y2   = 0
    self.dig_z1   = 0
    self.dig_z2   = 0
    self.dig_z3   = 0
    self.dig_z4   = 0
    self.dig_xy1  = 0
    self.dig_xy2  = 0
    self.dig_xyz1 = 0
_trim_data = trim_register()

class geomagnetic_data:
  def __init__(self):
    self.x   = 0
    self.y   = 0
    self.z   = 0
    self.r   = 0
_geomagnetic = geomagnetic_data()

class bmm150(object):
  PI                             = 3.141592653
  ENABLE_POWER                   = 1
  DISABLE_POWER                  = 0
  POLARITY_HIGH                  = 1
  POLARITY_LOW                   = 0
  ERROR                          = -1
  SELF_TEST_XYZ_FALL             = 0
  SELF_TEST_YZ_FAIL              = 1
  SELF_TEST_XZ_FAIL              = 2
  SELF_TEST_Z_FAIL               = 3
  SELF_TEST_XY_FAIL              = 4
  SELF_TEST_Y_FAIL               = 5
  SELF_TEST_X_FAIL               = 6
  SELF_TEST_XYZ_OK               = 7
  DRDY_ENABLE                    = 1
  DRDY_DISABLE                   = 0
  INTERRUPUT_LATCH_ENABLE        = 1
  INTERRUPUT_LATCH_DISABLE       = 0
  MEASUREMENT_X_ENABLE           = 0
  MEASUREMENT_Y_ENABLE           = 0
  MEASUREMENT_Z_ENABLE           = 0
  MEASUREMENT_X_DISABLE          = 1
  MEASUREMENT_Y_DISABLE          = 1
  MEASUREMENT_Z_DISABLE          = 1
  DATA_OVERRUN_ENABLE            = 1
  DATA_OVERRUN_DISABLE           = 0
  OVERFLOW_INT_ENABLE            = 1
  OVERFLOW_INT_DISABLE           = 0
  INTERRUPT_X_ENABLE             = 0
  INTERRUPT_Y_ENABLE             = 0
  INTERRUPT_Z_ENABLE             = 0
  INTERRUPT_X_DISABLE            = 1
  INTERRUPT_Y_DISABLE            = 1
  INTERRUPT_Z_DISABLE            = 1
  
  CHANNEL_X                      = 1
  CHANNEL_Y                      = 2
  CHANNEL_Z                      = 3
  ENABLE_INTERRUPT_PIN           = 1
  DISABLE_INTERRUPT_PIN          = 0
  POWERMODE_NORMAL               = 0x00
  POWERMODE_FORCED               = 0x01
  POWERMODE_SLEEP                = 0x03
  POWERMODE_SUSPEND              = 0x04
  PRESETMODE_LOWPOWER            = 0x01
  PRESETMODE_REGULAR             = 0x02
  PRESETMODE_HIGHACCURACY        = 0x03
  PRESETMODE_ENHANCED            = 0x04
  REPXY_LOWPOWER                 = 0x01
  REPXY_REGULAR                  = 0x04
  REPXY_ENHANCED                 = 0x07
  REPXY_HIGHACCURACY             = 0x17
  REPZ_LOWPOWER                  = 0x01
  REPZ_REGULAR                   = 0x07
  REPZ_ENHANCED                  = 0x0D
  REPZ_HIGHACCURACY              = 0x29
  CHIP_ID_VALUE                  = 0x32
  CHIP_ID_REGISTER               = 0x40
  REG_DATA_X_LSB                 = 0x42
  REG_DATA_READY_STATUS          = 0x48
  REG_INTERRUPT_STATUS           = 0x4a
  CTRL_POWER_REGISTER            = 0x4b
  MODE_RATE_REGISTER             = 0x4c
  REG_INT_CONFIG                 = 0x4D
  REG_AXES_ENABLE                = 0x4E
  REG_LOW_THRESHOLD              = 0x4F
  REG_HIGH_THRESHOLD             = 0x50
  REG_REP_XY                     = 0x51
  REG_REP_Z                      = 0x52
  RATE_10HZ                      = 0x00        #(default rate)
  RATE_02HZ                      = 0x01
  RATE_06HZ                      = 0x02
  RATE_08HZ                      = 0x03
  RATE_15HZ                      = 0x04
  RATE_20HZ                      = 0x05
  RATE_25HZ                      = 0x06
  RATE_30HZ                      = 0x07
  DIG_X1                         = 0x5D
  DIG_Y1                         = 0x5E
  DIG_Z4_LSB                     = 0x62
  DIG_Z4_MSB                     = 0x63
  DIG_X2                         = 0x64
  DIG_Y2                         = 0x65
  DIG_Z2_LSB                     = 0x68
  DIG_Z2_MSB                     = 0x69
  DIG_Z1_LSB                     = 0x6A
  DIG_Z1_MSB                     = 0x6B
  DIG_XYZ1_LSB                   = 0x6C
  DIG_XYZ1_MSB                   = 0x6D
  DIG_Z3_LSB                     = 0x6E
  DIG_Z3_MSB                     = 0x6F
  DIG_XY2                        = 0x70
  DIG_XY1                        = 0x71
  LOW_THRESHOLD_INTERRUPT        = 0x00
  HIGH_THRESHOLD_INTERRUPT       = 0x01
  NO_DATA                        = -32768
  __txbuf          = [0]          # i2c send buffer
  __threshold_mode = 2

  def __init__(self, sdaPin, sclPin):
    timeout = utime.time() + 10 # 10 sec
    while True:  
      self.i2cbus = SoftI2C(scl=Pin(sclPin), sda=Pin(sdaPin))
      if len(self.i2cbus.scan()) > 0 or utime.time() > timeout:
        break
      utime.sleep_ms(100)

  def sensor_init(self):
    '''!
      @brief Init bmm150 check whether the chip id is right
      @return 0  is init success
              -1 is init failed
    '''
    self.set_power_bit(self.ENABLE_POWER)
    chip_id = self.get_chip_id()
    if chip_id == self.CHIP_ID_VALUE:
      self.get_trim_data()
      return 0
    else:
      return -1

  def get_chip_id(self):
    '''!
      @brief get bmm150 chip id
      @return chip id
    '''
    rslt = self.read_reg(self.CHIP_ID_REGISTER, 1)
    return rslt[0]

  def soft_reset(self):
    '''!
      @brief Soft reset, restore to suspend mode after soft reset and then enter sleep mode
    '''
    rslt = self.read_reg(self.CTRL_POWER_REGISTER, 1)
    self.__txbuf[0] = rslt[0] | 0x82
    self.write_reg(self.CTRL_POWER_REGISTER, self.__txbuf)

  def set_power_bit(self, ctrl):
    '''!
      @brief Enable or disable power
      @param ctrl is enable/disable power
    '''
    rslt = self.read_reg(self.CTRL_POWER_REGISTER, 1)
    if ctrl == self.DISABLE_POWER:
      self.__txbuf[0] = rslt[0] & 0xFE
      self.write_reg(self.CTRL_POWER_REGISTER, self.__txbuf)
    else:
      self.__txbuf[0] = rslt[0] | 0x01
      self.write_reg(self.CTRL_POWER_REGISTER, self.__txbuf)

  def get_power_bit(self):
    '''!
      @brief Get the power state
      @return power state
    '''
    rslt = self.read_reg(self.CTRL_POWER_REGISTER, 1)
    return rslt[0] & 0x01

  def set_operation_mode(self, modes):
    '''!
      @brief Set sensor operation mode
      @param modes POWERMODE_NORMAL, POWERMODE_FORCED, POWERMODE_SLEEP, POWERMODE_SUSPEND
    '''
    rslt = self.read_reg(self.MODE_RATE_REGISTER, 1)
    if modes == self.POWERMODE_NORMAL:
      self.set_power_bit(self.ENABLE_POWER)
      rslt[0] = rslt[0] & 0xf9
      self.write_reg(self.MODE_RATE_REGISTER, rslt)
    elif modes == self.POWERMODE_FORCED:
      rslt[0] = (rslt[0] & 0xf9) | 0x02
      self.set_power_bit(self.ENABLE_POWER)
      self.write_reg(self.MODE_RATE_REGISTER, rslt)
    elif modes == self.POWERMODE_SLEEP:
      self.set_power_bit(self.ENABLE_POWER)
      rslt[0] = (rslt[0] & 0xf9) | 0x04
      self.write_reg(self.MODE_RATE_REGISTER, rslt)
    else:
      self.set_power_bit(self.DISABLE_POWER)

  def set_rate(self, rates):
    '''!
      @brief Set the rate of obtaining geomagnetic data
      @param rates RATE_02HZ to RATE_30HZ
    '''
    rslt = self.read_reg(self.MODE_RATE_REGISTER, 1)
    if rates == self.RATE_10HZ:
      rslt[0] = rslt[0] & 0xc7
    elif rates == self.RATE_02HZ:
      rslt[0] = (rslt[0] & 0xc7) | 0x08
    elif rates == self.RATE_06HZ:
      rslt[0] = (rslt[0] & 0xc7) | 0x10
    elif rates == self.RATE_08HZ:
      rslt[0] = (rslt[0] & 0xc7) | 0x18
    elif rates == self.RATE_15HZ:
      rslt[0] = (rslt[0] & 0xc7) | 0x20
    elif rates == self.RATE_20HZ:
      rslt[0] = (rslt[0] & 0xc7) | 0x28
    elif rates == self.RATE_25HZ:
      rslt[0] = (rslt[0] & 0xc7) | 0x30
    elif rates == self.RATE_30HZ:
      rslt[0] = (rslt[0] & 0xc7) | 0x38
    else:
      rslt[0] = rslt[0] & 0xc7
    self.write_reg(self.MODE_RATE_REGISTER, rslt)

  def set_preset_mode(self, modes):
    '''!
      @brief Set preset mode for accuracy
      @param modes PRESETMODE_LOWPOWER, PRESETMODE_REGULAR, PRESETMODE_HIGHACCURACY, PRESETMODE_ENHANCED
    '''
    if modes == self.PRESETMODE_LOWPOWER:
      self.set_xy_rep(self.REPXY_LOWPOWER)
      self.set_z_rep(self.REPZ_LOWPOWER)
    elif modes == self.PRESETMODE_REGULAR:
      self.set_xy_rep(self.REPXY_REGULAR)
      self.set_z_rep(self.REPZ_REGULAR)
    elif modes == self.PRESETMODE_HIGHACCURACY:
      self.set_xy_rep(self.REPXY_HIGHACCURACY)
      self.set_z_rep(self.REPZ_HIGHACCURACY)
    elif modes == self.PRESETMODE_ENHANCED:
      self.set_xy_rep(self.REPXY_ENHANCED)
      self.set_z_rep(self.REPZ_ENHANCED)
    else:
      self.set_xy_rep(self.REPXY_LOWPOWER)
      self.set_z_rep(self.REPZ_LOWPOWER)

  def set_xy_rep(self, modes):
    '''!
      @brief the number of repetitions for x/y-axis
    '''
    self.__txbuf[0] = modes
    self.write_reg(self.REG_REP_XY, self.__txbuf)

  def set_z_rep(self, modes):
    '''!
      @brief the number of repetitions for z-axis
    '''
    self.__txbuf[0] = modes
    self.write_reg(self.REG_REP_Z, self.__txbuf)

  def get_trim_data(self):
    '''!
      @brief Get bmm150 reserved data information for compensation
    '''
    trim_x1_y1    = self.read_reg(self.DIG_X1, 2)
    trim_xyz_data = self.read_reg(self.DIG_Z4_LSB, 4)
    trim_xy1_xy2  = self.read_reg(self.DIG_Z2_LSB, 10)
    _trim_data.dig_x1 = self.uint8_to_int8(trim_x1_y1[0])
    _trim_data.dig_y1 = self.uint8_to_int8(trim_x1_y1[1])
    _trim_data.dig_x2 = self.uint8_to_int8(trim_xyz_data[2])
    _trim_data.dig_y2 = self.uint8_to_int8(trim_xyz_data[3])
    temp_msb = int(trim_xy1_xy2[3]) << 8
    _trim_data.dig_z1 = int(temp_msb | trim_xy1_xy2[2])
    temp_msb = int(trim_xy1_xy2[1] << 8)
    _trim_data.dig_z2 = int(temp_msb | trim_xy1_xy2[0])
    temp_msb = int(trim_xy1_xy2[7] << 8)
    _trim_data.dig_z3 = temp_msb | trim_xy1_xy2[6]
    temp_msb = int(trim_xyz_data[1] << 8)
    _trim_data.dig_z4 = int(temp_msb | trim_xyz_data[0])
    _trim_data.dig_xy1 = trim_xy1_xy2[9]
    _trim_data.dig_xy2 = self.uint8_to_int8(trim_xy1_xy2[8])
    temp_msb = int((trim_xy1_xy2[5] & 0x7F) << 8)
    _trim_data.dig_xyz1 = int(temp_msb | trim_xy1_xy2[4])

  def get_geomagnetic(self):
    '''!
      @brief Get the geomagnetic data of 3 axis (x, y, z)
      @return The list of the geomagnetic data at 3 axis (x, y, z) unit: uT
    '''
    rslt = self.read_reg(self.REG_DATA_X_LSB, 8)
    rslt[1] = self.uint8_to_int8(rslt[1])
    rslt[3] = self.uint8_to_int8(rslt[3])
    rslt[5] = self.uint8_to_int8(rslt[5])
    _geomagnetic.x = ((rslt[0] & 0xF8) >> 3) | int(rslt[1] * 32)
    _geomagnetic.y = ((rslt[2] & 0xF8) >> 3) | int(rslt[3] * 32)
    _geomagnetic.z = ((rslt[4] & 0xFE) >> 1) | int(rslt[5] * 128)
    _geomagnetic.r = ((rslt[6] & 0xFC) >> 2) | int(rslt[7] * 64)
    rslt[0] = self.compenstate_x(_geomagnetic.x, _geomagnetic.r)
    rslt[1] = self.compenstate_y(_geomagnetic.y, _geomagnetic.r)
    rslt[2] = self.compenstate_z(_geomagnetic.z, _geomagnetic.r)
    return rslt

  def get_compass_degree(self):
    '''!
      @brief Get compass degree
      @return Compass degree (0° - 360°)  0° = North, 90° = East, 180° = South, 270° = West.
    '''
    geomagnetic = self.get_geomagnetic()
    compass = math.atan2(geomagnetic[0], geomagnetic[1])
    if compass < 0:
      compass += 2 * self.PI
    if compass > 2 * self.PI:
      compass -= 2 * self.PI
    return compass * 180 / self.PI

  def uint8_to_int8(self, number):
    '''!
      @brief uint8_t to int8_t
    '''
    if number <= 127:
      return number
    else:
      return (256 - number) * -1

  def compenstate_x(self, data_x, data_r):
    '''!
      @brief Compensate the geomagnetic data at x-axis
    '''
    if data_x != -4096:
      if data_r != 0:
        process_comp_x0 = data_r
      elif _trim_data.dig_xyz1 != 0:
        process_comp_x0 = _trim_data.dig_xyz1
      else:
        process_comp_x0 = 0
      if process_comp_x0 != 0:
        process_comp_x1 = int(_trim_data.dig_xyz1 * 16384)
        process_comp_x2 = int(process_comp_x1 / process_comp_x0 - 0x4000)
        retval = process_comp_x2
        process_comp_x3 = retval * retval
        process_comp_x4 = _trim_data.dig_xy2 * (process_comp_x3 / 128)
        process_comp_x5 = _trim_data.dig_xy1 * 128
        process_comp_x6 = retval * process_comp_x5
        process_comp_x7 = (process_comp_x4 + process_comp_x6) / 512 + 0x100000
        process_comp_x8 = _trim_data.dig_x2 + 0xA0
        process_comp_x9 = (process_comp_x8 * process_comp_x7) / 4096
        process_comp_x10 = data_x * process_comp_x9
        retval = process_comp_x10 / 8192
        retval = (retval + _trim_data.dig_x1 * 8) / 16
      else:
        retval = -32368
    else:
      retval = -32768
    return retval

  def compenstate_y(self, data_y, data_r):
    '''!
      @brief Compensate the geomagnetic data at y-axis
    '''
    if data_y != -4096:
      if data_r != 0:
        process_comp_y0 = data_r
      elif _trim_data.dig_xyz1 != 0:
        process_comp_y0 = _trim_data.dig_xyz1
      else:
        process_comp_y0 = 0
      if process_comp_y0 != 0:
        process_comp_y1 = int(_trim_data.dig_xyz1 * 16384 / process_comp_y0)
        process_comp_y2 = int(process_comp_y1 - 0x4000)
        retval = process_comp_y2
        process_comp_y3 = retval * retval
        process_comp_y4 = _trim_data.dig_xy2 * (process_comp_y3 / 128)
        process_comp_y5 = _trim_data.dig_xy1 * 128
        process_comp_y6 = (process_comp_y4 + process_comp_y5 * retval) / 512
        process_comp_y7 = _trim_data.dig_y2 + 0xA0
        process_comp_y8 = ((process_comp_y6 + 0x100000) * process_comp_y7) / 4096
        process_comp_y9 = data_y * process_comp_y8
        retval = process_comp_y9 / 8192
        retval = (retval + _trim_data.dig_y1 * 8) / 16
      else:
        retval = -32368
    else:
      retval = -32768
    return retval

  def compenstate_z(self, data_z, data_r):
    '''!
      @brief Compensate the geomagnetic data at z-axis
    '''
    if data_z != -16348:
      if _trim_data.dig_z2 != 0 and _trim_data.dig_z1 != 0 and _trim_data.dig_xyz1 != 0 and data_r != 0:
        process_comp_z0 = data_r - _trim_data.dig_xyz1
        process_comp_z1 = (_trim_data.dig_z3 * process_comp_z0) / 4
        process_comp_z2 = (data_z - _trim_data.dig_z4) * 32768
        process_comp_z3 = _trim_data.dig_z1 * data_r * 2
        process_comp_z4 = (process_comp_z3 + 32768) / 65536
        retval = (process_comp_z2 - process_comp_z1) / (_trim_data.dig_z2 + process_comp_z4)
        if retval > 32767:
          retval = 32367
        elif retval < -32367:
          retval = -32367
        retval = retval / 16
      else:
        retval = -32768
    else:
      retval = -32768
    return retval

  def set_measurement_xyz(self, channel_x=MEASUREMENT_X_ENABLE, channel_y=MEASUREMENT_Y_ENABLE, channel_z=MEASUREMENT_Z_ENABLE):
    '''!
      @brief Enable the measurement at x-axis, y-axis and z-axis
    '''
    rslt = self.read_reg(self.REG_AXES_ENABLE, 1)
    if channel_x == self.MEASUREMENT_X_DISABLE:
      self.__txbuf[0] = rslt[0] | 0x08
    else:
      self.__txbuf[0] = rslt[0] & 0xF7
    if channel_y == self.MEASUREMENT_Y_DISABLE:
      self.__txbuf[0] = self.__txbuf[0] | 0x10
    else:
      self.__txbuf[0] = self.__txbuf[0] & 0xEF
    if channel_z == self.MEASUREMENT_Z_DISABLE:
      self.__txbuf[0] = self.__txbuf[0] | 0x20
    else:
      self.__txbuf[0] = self.__txbuf[0] & 0xDF
    self.write_reg(self.REG_AXES_ENABLE, self.__txbuf)


class bmm150_I2C(bmm150): 
  '''!
    @brief An example of an i2c interface module
  '''
  ADDRESS_0 = 0x10  # (CSB:0 SDO:0)
  ADDRESS_1 = 0x11  # (CSB:0 SDO:1)
  ADDRESS_2 = 0x12  # (CSB:1 SDO:0)
  ADDRESS_3 = 0x13  # (CSB:1 SDO:1) default i2c address
  
  def __init__(self, addr=ADDRESS_3, sdaPin=0, sclPin=1, retries=5, delay=1):
    self.__addr = addr
    self.sdaPin = sdaPin
    self.sclPin = sclPin
    self.retries = retries
    self.delay = delay
    
    for attempt in range(self.retries):
      try:
        # Appel du constructeur de la classe mère
        super(bmm150_I2C, self).__init__(self.sdaPin, self.sclPin)
        
        # Initialisation avec sensor_init() pour lire les données de calibration
        if self.sensor_init() == 0:
          self.set_operation_mode(bmm150.POWERMODE_NORMAL)
          self.set_preset_mode(bmm150.PRESETMODE_HIGHACCURACY)
          self.set_rate(bmm150.RATE_10HZ)
          self.set_measurement_xyz()
        break
      except OSError as e:
        if attempt < self.retries - 1:
          utime.sleep(self.delay)
        else:
          print("bmm150 : Échec après plusieurs tentatives.")
          raise

  def write_reg(self, reg, data):
    '''!
      @brief writes data to a register
    '''
    if isinstance(data, int):
      self.i2cbus.writeto_mem(self.__addr, reg, data.to_bytes(1, 'little'))
    else:
      for i in data:
        self.i2cbus.writeto_mem(self.__addr, reg, i.to_bytes(1, 'little'))
  
  def read_reg(self, reg, length):
    '''!
      @brief read the data from the register
    '''
    if length == 1:
      return list(self.i2cbus.readfrom_mem(self.__addr, reg, 1))
    else:
      return list(self.i2cbus.readfrom_mem(self.__addr, reg, length))

  def get_geomagnetic(self):
    '''!
      @brief Get geomagnetic data with soft reset for fresh readings
    '''
    # Soft reset requis AVANT CHAQUE lecture pour obtenir des données fraîches
    self.set_power_bit(bmm150.DISABLE_POWER)
    utime.sleep_ms(10)
    self.set_power_bit(bmm150.ENABLE_POWER)
    utime.sleep_ms(10)
    self.set_operation_mode(bmm150.POWERMODE_NORMAL)
    utime.sleep_ms(50)
    return super().get_geomagnetic()
