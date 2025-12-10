import utime
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
  
  # Chip ID
  BMM150_CHIP_ID                 = 0x32
  
  # SPI 4-wire mode
  SPI_RD                         = 0x80
  
  # Power mode settings
  POWERMODE_NORMAL               = 0x00
  POWERMODE_FORCED               = 0x01
  POWERMODE_SLEEP                = 0x03
  POWERMODE_SUSPEND              = 0x04
  
  # PRESET MODE DEFINITIONS
  PRESETMODE_LOWPOWER            = 0x01
  PRESETMODE_REGULAR             = 0x02
  PRESETMODE_HIGHACCURACY        = 0x03
  PRESETMODE_ENHANCED            = 0x04
  
  # Data rate
  RATE_10HZ                      = 0x00
  RATE_02HZ                      = 0x01
  RATE_06HZ                      = 0x02
  RATE_08HZ                      = 0x03
  RATE_15HZ                      = 0x04
  RATE_20HZ                      = 0x05
  RATE_25HZ                      = 0x06
  RATE_30HZ                      = 0x07
  
  # Measurement enable
  MEASUREMENT_X_ENABLE           = 0x00
  MEASUREMENT_Y_ENABLE           = 0x00
  MEASUREMENT_Z_ENABLE           = 0x00
  MEASUREMENT_X_DISABLE          = 0x01
  MEASUREMENT_Y_DISABLE          = 0x01
  MEASUREMENT_Z_DISABLE          = 0x01
  
  # Interrupt enable
  ENABLE_INTERRUPT_PIN           = 0x01
  DISABLE_INTERRUPT_PIN          = 0x00
  
  # Interrupt polarity
  POLARITY_HIGH                  = 0x01
  POLARITY_LOW                   = 0x00
  
  # Interrupt latch
  INTERRUPUT_LATCH_ENABLE        = 0x01
  INTERRUPUT_LATCH_DISABLE       = 0x00
  
  # Threshold interrupt
  LOW_THRESHOLD_INTERRUPT        = 0x00
  HIGH_THRESHOLD_INTERRUPT       = 0x01
  
  # Interrupt x/y/z axis enable
  INTERRUPT_X_ENABLE             = 0x00
  INTERRUPT_Y_ENABLE             = 0x00
  INTERRUPT_Z_ENABLE             = 0x00
  INTERRUPT_X_DISABLE            = 0x01
  INTERRUPT_Y_DISABLE            = 0x01
  INTERRUPT_Z_DISABLE            = 0x01
  
  HIGH_INTERRUPT_X_DISABLE       = 0x01
  HIGH_INTERRUPT_Y_DISABLE       = 0x01
  HIGH_INTERRUPT_Z_DISABLE       = 0x01
  
  # Threshold value
  NO_DATA                        = -32768
  
  # Register map
  REG_CHIP_ID                    = 0x40
  REG_DATA_X_LSB                 = 0x42
  REG_DATA_X_MSB                 = 0x43
  REG_DATA_Y_LSB                 = 0x44
  REG_DATA_Y_MSB                 = 0x45
  REG_DATA_Z_LSB                 = 0x46
  REG_DATA_Z_MSB                 = 0x47
  REG_DATA_R_LSB                 = 0x48
  REG_DATA_R_MSB                 = 0x49
  REG_INTERRUPT_STATUS           = 0x4A
  REG_POWER_CONTROL              = 0x4B
  REG_OP_MODE                    = 0x4C
  REG_INT_CONFIG                 = 0x4D
  REG_AXES_ENABLE                = 0x4E
  REG_LOW_THRESHOLD              = 0x4F
  REG_HIGH_THRESHOLD             = 0x50
  
  # Trim registers
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
  
  __threshold_mode                = LOW_THRESHOLD_INTERRUPT
  __txbuf        = [0]
  
  def __init__(self, sda_1=0, scl_1=0):
    pass
    
  def sensor_init(self):
    '''!
      @brief Initialize the sensor, detection sensor, read trim data, set the power mode to normal mode, enable the measurement of x/y/z axis, set the rate to 10Hz
      @return Return 0 if initialization succeeds, otherwise return non-zero
    '''
    self.set_power_bit(self.ENABLE_POWER)
    rslt = self.read_reg(self.REG_CHIP_ID, 1)
    if rslt[0] == self.BMM150_CHIP_ID:
      self.read_trim_registers()
      self.set_operation_mode(self.POWERMODE_NORMAL)
      self.set_preset_mode(self.PRESETMODE_HIGHACCURACY)
      self.set_rate(self.RATE_10HZ)
      self.set_measurement_xyz()
      return 0
    else:
      return 1

  def read_trim_registers(self):
    '''!
      @brief Read the trim data of the sensor
    '''
    trim_x1_y1 = self.read_reg(self.DIG_X1, 2)
    trim_xyz_data = self.read_reg(self.DIG_Z4_LSB, 4)
    trim_xy1_xy2 = self.read_reg(self.DIG_Z2_LSB, 10)
    
    _trim_data.dig_x1 = self.uint8_to_int8(trim_x1_y1[0])
    _trim_data.dig_y1 = self.uint8_to_int8(trim_x1_y1[1])
    _trim_data.dig_x2 = self.uint8_to_int8(trim_xyz_data[2])
    _trim_data.dig_y2 = self.uint8_to_int8(trim_xyz_data[3])
    _trim_data.dig_z1 = (trim_xy1_xy2[3]<<8)| trim_xy1_xy2[2]
    _trim_data.dig_z2 = (trim_xy1_xy2[1]<<8)| trim_xy1_xy2[0]
    _trim_data.dig_z3 = (trim_xy1_xy2[7]<<8)| trim_xy1_xy2[6]
    _trim_data.dig_z4 = (trim_xyz_data[1]<<8)| trim_xyz_data[0]
    _trim_data.dig_xy1 = trim_xy1_xy2[9]
    _trim_data.dig_xy2 = self.uint8_to_int8(trim_xy1_xy2[8])
    _trim_data.dig_xyz1 = (trim_xy1_xy2[5] & 0x7F)<<8 | trim_xy1_xy2[4]

  def uint8_to_int8(self, number):
    '''!
      @brief Convert 8-bit unsigned integer to 8-bit signed integer
      @param number 8-bit unsigned integer
      @return 8-bit signed integer
    '''
    if number <= 127:
      return number
    else:
      return number - 256
      
  def set_power_bit(self, ctrl_bit):
    '''!
      @brief Enable or disable power
      @param ctrl_bit
      @n ENABLE_POWER     Enable power
      @n DISABLE_POWER    Disable power
    '''
    self.__txbuf[0] = ctrl_bit & 0x01
    self.write_reg(self.REG_POWER_CONTROL, self.__txbuf)
  
  def set_operation_mode(self, modes):
    '''!
      @brief Set the power mode of the sensor
      @param modes
      @n POWERMODE_NORMAL       Normal mode, get data by reading the data of the register directly
      @n POWERMODE_FORCED       Forced mode, send commands to the register to provoke a single measurement
      @n POWERMODE_SLEEP        Sleep mode, the sensor is in idle status
      @n POWERMODE_SUSPEND      Suspend mode, the sensor is in suspend status, and can only be woken up by calling set_power_bit(self.ENABLE_POWER)
    '''
    rslt = self.read_reg(self.REG_OP_MODE, 1)
    if modes == self.POWERMODE_NORMAL:
      self.__txbuf[0] = rslt[0] & 0xF9
    elif modes == self.POWERMODE_FORCED:
       self.__txbuf[0] = (rslt[0] & 0xF9) | 0x02
    elif modes == self.POWERMODE_SLEEP:
       self.__txbuf[0] = (rslt[0] & 0xF9) | 0x06
    else:
       self.__txbuf[0] = rslt[0] & 0x7F
       self.set_power_bit(self.DISABLE_POWER)
       return 
    self.set_power_bit(self.ENABLE_POWER)
    self.write_reg(self.REG_OP_MODE, self.__txbuf)

  def set_preset_mode(self, modes):
    '''!
      @brief Set the preset mode of the sensor
      @param modes
      @n PRESETMODE_LOWPOWER       Low power mode, get a fraction of data, the mean value of 2 measurements
      @n PRESETMODE_REGULAR        Regular mode, get a fraction of data, the mean value of 4 measurements
      @n PRESETMODE_HIGHACCURACY   High accuracy mode, get a fraction of data, the mean value of 10 measurements
      @n PRESETMODE_ENHANCED       Enhanced mode, get a fraction of data, the mean value of 20 measurements
    '''
    if modes == self.PRESETMODE_LOWPOWER:
      self.set_rep_xy(0x01)
      self.set_rep_z(0x02)
    elif modes == self.PRESETMODE_REGULAR:
      self.set_rep_xy(0x04)
      self.set_rep_z(0x0E)
    elif modes == self.PRESETMODE_HIGHACCURACY:
      self.set_rep_xy(0x17)
      self.set_rep_z(0x29)
    elif modes == self.PRESETMODE_ENHANCED:
      self.set_rep_xy(0x17)
      self.set_rep_z(0x51)
    else:
      self.set_rep_xy(0x04)
      self.set_rep_z(0x0E)

  def set_rate(self, rates):
    '''!
      @brief Set the data rate of the sensor
      @param rates
      @n RATE_10HZ        Data rate 10Hz
      @n RATE_02HZ        Data rate 2Hz
      @n RATE_06HZ        Data rate 6Hz
      @n RATE_08HZ        Data rate 8Hz
      @n RATE_15HZ        Data rate 15Hz
      @n RATE_20HZ        Data rate 20Hz
      @n RATE_25HZ        Data rate 25Hz
      @n RATE_30HZ        Data rate 30Hz
    '''
    rslt = self.read_reg(self.REG_OP_MODE, 1)
    if rates == self.RATE_10HZ:
      self.__txbuf[0] = rslt[0] & 0xC7
    elif rates == self.RATE_02HZ:
      self.__txbuf[0] = (rslt[0] & 0xC7) | 0x08
    elif rates == self.RATE_06HZ:
      self.__txbuf[0] = (rslt[0] & 0xC7) | 0x10
    elif rates == self.RATE_08HZ:
      self.__txbuf[0] = (rslt[0] & 0xC7) | 0x18
    elif rates == self.RATE_15HZ:
      self.__txbuf[0] = (rslt[0] & 0xC7) | 0x20
    elif rates == self.RATE_20HZ:
      self.__txbuf[0] = (rslt[0] & 0xC7) | 0x28
    elif rates == self.RATE_25HZ:
      self.__txbuf[0] = (rslt[0] & 0xC7) | 0x30
    elif rates == self.RATE_30HZ:
      self.__txbuf[0] = (rslt[0] & 0xC7) | 0x38
    else:
      self.__txbuf[0] = rslt[0] & 0xC7
    self.write_reg(self.REG_OP_MODE, self.__txbuf)
  
  def set_rep_xy(self, rep_xy):
    '''!
      @brief Set the xy-axis repetition of the sensor
      @param rep_xy xy-axis repetition
    '''
    self.__txbuf[0] = rep_xy
    self.write_reg(0x51, self.__txbuf)

  def set_rep_z(self, rep_z):
    '''!
      @brief Set the z-axis repetition of the sensor
      @param rep_z z-axis repetition
    '''
    self.__txbuf[0] = rep_z
    self.write_reg(0x52, self.__txbuf)

  def get_geomagnetic(self):
    '''!
      @brief Get the geomagnetic data
      @return Return the list of the geomagnetic data
      @n      [0] x-axis geomagnetic data
      @n      [1] y-axis geomagnetic data
      @n      [2] z-axis geomagnetic data
    '''
    data = [0,0,0]
    rslt = self.read_reg(self.REG_DATA_X_LSB, 8)
    
    rslt[0] = self.uint8_to_int8(rslt[0])
    rslt[1] = self.uint8_to_int8(rslt[1])
    rslt[2] = self.uint8_to_int8(rslt[2])
    rslt[3] = self.uint8_to_int8(rslt[3])
    rslt[4] = self.uint8_to_int8(rslt[4])
    rslt[5] = self.uint8_to_int8(rslt[5])
    rslt[6] = self.uint8_to_int8(rslt[6])
    rslt[7] = self.uint8_to_int8(rslt[7])
    
    lsb = rslt[0] & 0x01
    
    msb = (rslt[0] & 0xF8) if lsb == 0 else (rslt[0] | 0x07)
    
    temp = (rslt[1]<<5)|(msb>>3)
    if temp > 4095:
      _geomagnetic.x = temp - 8192
    else:
      _geomagnetic.x = temp
  
    lsb = rslt[2] & 0x01
    msb = (rslt[2] & 0xF8) if lsb == 0 else (rslt[2] | 0x07)
    temp = (rslt[3]<<5)|(msb>>3)
    if temp > 4095:
      _geomagnetic.y = temp - 8192
    else:
      _geomagnetic.y = temp

    lsb = rslt[4] & 0x01
    msb = (rslt[4] & 0xF8) if lsb == 0 else (rslt[4] | 0x07)
    temp = (rslt[5]<<7)|(msb>>1)
    if temp > 16383:
      _geomagnetic.z = temp - 32768
    else:
      _geomagnetic.z = temp

    lsb = rslt[6] & 0x01
    msb = (rslt[6] & 0xF8) if lsb == 0 else (rslt[6] | 0x07)
    temp = (rslt[7]<<6)|(msb>>2)
    if temp > 8191:
      _geomagnetic.r = temp - 16384
    else:
      _geomagnetic.r = temp
    
    data[0] = self.compensate_x(_geomagnetic.x, _geomagnetic.r)
    data[1] = self.compensate_y(_geomagnetic.y, _geomagnetic.r)
    data[2] = self.compensate_z(_geomagnetic.z, _geomagnetic.r)
    return data
    
  def compensate_x(self, mag_data_x, data_r):
    '''!
      @brief Compensate the x-axis geomagnetic data
      @param mag_data_x x-axis geomagnetic data
      @param data_r     resistance data
      @return Return the compensated x-axis geomagnetic data
    '''
    if mag_data_x != -4096:
      if data_r != 0:
        process_comp_x0 = _trim_data.dig_xyz1 * 16384
        process_comp_x1 = (process_comp_x0 / data_r) - 16384
        process_comp_x2 = process_comp_x1 + _trim_data.dig_xy2
        retval = mag_data_x * ((process_comp_x2 * process_comp_x2 / 268435456 + mag_data_x * _trim_data.dig_xy1 / 16384) + 256 * (_trim_data.dig_x2 + 160))
        return (retval / 8192 + _trim_data.dig_x1 * 8) / 16
      else:
        return -32768
    else:
      return -32768

  def compensate_y(self, mag_data_y, data_r):
    '''!
      @brief Compensate the y-axis geomagnetic data
      @param mag_data_y y-axis geomagnetic data
      @param data_r     resistance data
      @return Return the compensated y-axis geomagnetic data
    '''
    if mag_data_y != -4096:
      if data_r != 0:
        process_comp_y0 = _trim_data.dig_xyz1 * 16384
        process_comp_y1 = (process_comp_y0 / data_r) - 16384
        process_comp_y2 = process_comp_y1 + _trim_data.dig_xy2
        retval = mag_data_y * ((process_comp_y2 * process_comp_y2 / 268435456 + mag_data_y * _trim_data.dig_xy1 / 16384) + 256 * (_trim_data.dig_y2 + 160))
        return (retval / 8192 + _trim_data.dig_y1 * 8) / 16
      else:
        return -32768
    else:
      return -32768

  def compensate_z(self, mag_data_z, data_r):
    '''!
      @brief Compensate the z-axis geomagnetic data
      @param mag_data_z z-axis geomagnetic data
      @param data_r     resistance data
      @return Return the compensated z-axis geomagnetic data
    '''
    if mag_data_z != -16384:
       process_comp_z0 = ((data_r - _trim_data.dig_xyz1) * 16384) / 4
       process_comp_z1 = (mag_data_z - _trim_data.dig_z4) * 32768
       process_comp_z2 = _trim_data.dig_z3 * process_comp_z0
       process_comp_z3 = ((_trim_data.dig_z1 * (data_r * 2)) / 65536) * 32768
       process_comp_z4 = _trim_data.dig_z2 * (process_comp_z0 * 32768 / 4096)
       process_comp_z5 = (process_comp_z1 * 128) + (process_comp_z2 * 2) + (process_comp_z3 * 8192) + (process_comp_z4 * 2048)
       retval = process_comp_z5 / (65536 + _trim_data.dig_z2 * process_comp_z0 / 4096)
       return (retval / 16) / 4
    else:
       return -32768

  def get_compass_degree(self):
    '''!
      @brief Get the compass degree
      @return Return the compass degree
    '''
    mag_data = self.get_geomagnetic()
    azimuth = math.atan2(mag_data[1], mag_data[0]) * 180 / self.PI
    if azimuth < 0:
      azimuth = azimuth + 360
    return azimuth

  def set_measurement_xyz(self, channel_x = MEASUREMENT_X_ENABLE, channel_y = MEASUREMENT_Y_ENABLE, channel_z = MEASUREMENT_Z_ENABLE):
    '''!
      @brief Enable the measurement at x-axis, y-axis and z-axis, default to be enabled, no config required. When disabled, the geomagnetic data at x, y, and z will be inaccurate.
      @param channel_x
      @n MEASUREMENT_X_ENABLE     Enable the measurement at x-axis
      @n MEASUREMENT_X_DISABLE    Disable the measurement at x-axis
      @param channel_y
      @n MEASUREMENT_Y_ENABLE     Enable the measurement at y-axis
      @n MEASUREMENT_Y_DISABLE    Disable the measurement at y-axis
      @param channel_z
      @n MEASUREMENT_Z_ENABLE     Enable the measurement at z-axis
      @n MEASUREMENT_Z_DISABLE    Disable the measurement at z-axis
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

  def get_measurement_xyz_state(self):
    '''!
      @brief Get the enabling status at x-axis, y-axis and z-axis
      @return Return enabling status at x-axis, y-axis and z-axis as a character string
    '''
    str1 = ""
    rslt = self.read_reg(self.REG_AXES_ENABLE, 1)
    if (rslt[0]&0x08) == 0:
      str1 += "x "
    if (rslt[0]&0x10) == 0:
      str1 += "y "
    if (rslt[0]&0x20) == 0:
      str1 += "z "
    if str1 == "":
      str1 = "xyz aix not enable"
    else:
      str1 += "aix enable"
    return str1

  def set_interrupt_pin(self, modes, polarity):
    '''!
      @brief Enable or disable INT interrupt pin
      @n     Enabling pin will trigger interrupt pin INT level jump
      @n     After disabling pin, INT interrupt pin will not have level jump
      @n     High polarity: active on high, the default is low level, which turns to high level when the interrupt is triggered.
      @n     Low polarity: active on low, the default is high level, which turns to low level when the interrupt is triggered.
      @param modes
      @n     ENABLE_INTERRUPT_PIN     Enable interrupt pin
      @n     DISABLE_INTERRUPT_PIN    Disable interrupt pin
      @param polarity
      @n     POLARITY_HIGH            High polarity
      @n     POLARITY_LOW             Low polarity
    '''
    rslt = self.read_reg(self.REG_AXES_ENABLE, 1)
    if modes == self.DISABLE_INTERRUPT_PIN:
      self.__txbuf[0] = rslt[0] & 0xBF
    else:
      self.__txbuf[0] = rslt[0] | 0x40
    if polarity == self.POLARITY_LOW:
      self.__txbuf[0] = self.__txbuf[0] & 0xFE
    else:
      self.__txbuf[0] = self.__txbuf[0] | 0x01
    self.write_reg(self.REG_AXES_ENABLE, self.__txbuf)

  
  def set_interruput_latch(self, modes):
    '''!
      @brief Set interrupt latch mode, after enabling interrupt latch, the data can be refreshed only when the BMM150_REG_INTERRUPT_STATUS interrupt status register is read.
      @n   Disable interrupt latch, data update in real-time
      @param modes
      @n  INTERRUPUT_LATCH_ENABLE         Enable interrupt latch
      @n  INTERRUPUT_LATCH_DISABLE        Disable interrupt latch
    '''
    rslt = self.read_reg(self.REG_AXES_ENABLE, 1)
    if modes == self.INTERRUPUT_LATCH_DISABLE:
      self.__txbuf[0] = rslt[0] & 0xFD
    else:
      self.__txbuf[0] = rslt[0] | 0x02
    self.write_reg(self.REG_AXES_ENABLE, self.__txbuf)

  
  def set_threshold_interrupt(self, mode, threshold, polarity, channel_x = INTERRUPT_X_ENABLE, channel_y = INTERRUPT_Y_ENABLE, channel_z = INTERRUPT_Z_ENABLE):
    '''!
      @brief Set threshold interrupt, an interrupt is triggered when the geomagnetic value of a channel is beyond/below the threshold
      @n      High polarity: active on high, the default is low level, which turns to high level when the interrupt is triggered.
      @n      Low polarity: active on low, the default is high level, which turns to low level when the interrupt is triggered.
      @param mode
      @n     LOW_THRESHOLD_INTERRUPT     Low threshold interrupt mode
      @n     HIGH_THRESHOLD_INTERRUPT    High threshold interrupt mode
      @param threshold
      @n Threshold, default to expand 16 times, for example: under low threshold mode, if the threshold is set to be 1, actually the geomagnetic data below 16 will trigger an interrupt
      @param polarity
      @n POLARITY_HIGH               High polarity
      @n POLARITY_LOW                Low polarity
      @param channel_x
      @n INTERRUPT_X_ENABLE          Enable low threshold interrupt at x-axis
      @n INTERRUPT_X_DISABLE         Disable low threshold interrupt at x-axis
      @param channel_y
      @n INTERRUPT_Y_ENABLE          Enable low threshold interrupt at y-axis
      @n INTERRUPT_Y_DISABLE         Disable low threshold interrupt at y-axis
      @param channel_z
      @n INTERRUPT_Z_ENABLE          Enable low threshold interrupt at z-axis
      @n INTERRUPT_Z_DISABLE         Disable low threshold interrupt at z-axis
    '''
    if mode == self.LOW_THRESHOLD_INTERRUPT:
      self.__threshold_mode = self.LOW_THRESHOLD_INTERRUPT
      self.set_low_threshold_interrupt(channel_x, channel_y, channel_z, threshold, polarity)
    else:
      self.__threshold_mode = self.HIGH_THRESHOLD_INTERRUPT
      self.set_high_threshold_interrupt(channel_x, channel_y, channel_z, threshold, polarity)

  def get_threshold_interrupt_data(self):
    '''!
      @brief Get the data that threshold interrupt occured
      @return Return the list for storing geomagnetic data, how the data at 3 axis influence interrupt status,
      @n      [0] The data triggering threshold at x-axis, when the data is NO_DATA, the interrupt is triggered.
      @n      [1] The data triggering threshold at y-axis, when the data is NO_DATA, the interrupt is triggered.
      @n      [2] The data triggering threshold at z-axis, when the data is NO_DATA, the interrupt is triggered.
      @n      [3] The character string storing the trigger threshold interrupt status
      @n      [4] The binary data format of storing threshold interrupt status are as follows
      @n         bit0 is 1 indicate threshold interrupt is triggered at x-axis
      @n         bit1 is 1 indicate threshold interrupt is triggered at y-axis
      @n         bit2 is 1 indicate threshold interrupt is triggered at z-axis
      @n         ------------------------------------
      @n         | bit7 ~ bit3 | bit2 | bit1 | bit0 |
      @n         ------------------------------------
      @n         |  reserved   |  0   |  0   |  0   |
      @n         ------------------------------------
    '''
    data = [0]*10
    str1 = ""
    if self.__threshold_mode == self.LOW_THRESHOLD_INTERRUPT:
      state = self.get_low_threshold_interrupt_state()
    else:
      state = self.get_high_threshold_interrupt_state()
    rslt = self.get_geomagnetic()
    if (state>>0)&0x01:
      data[0] = rslt[0]
      str1 += "X "
    else:
      data[0] = self.NO_DATA
    if (state>>1)&0x01:
      data[1] = rslt[1]
      str1 += "Y "
    else:
      data[1] = self.NO_DATA
    if (state>>2)&0x01:
      data[2] = rslt[2]
      str1 += "Z "
    else:
      data[2] = self.NO_DATA
    if state != 0:
      str1 += " threshold interrupt"
    data[3] = str1
    data[4] = state&0x07
    
    return data
  
  def set_low_threshold_interrupt(self, channel_x, channel_y, channel_z, low_threshold, polarity):
    '''!
      @brief Set low threshold interrupt, an interrupt is triggered when the geomagnetic value of a channel is below the low threshold
      @n      High polarity: active on high, the default is low level, which turns to high level when the interrupt is triggered.
      @n      Low polarity: active on low, the default is high level, which turns to low level when the interrupt is triggered.
      @param channel_x
      @n     INTERRUPT_X_ENABLE          Enable low threshold interrupt at x-axis
      @n     INTERRUPT_X_DISABLE         Disable low threshold interrupt at x-axis
      @param channel_y
      @n     INTERRUPT_Y_ENABLE          Enable low threshold interrupt at y-axis
      @n     INTERRUPT_Y_DISABLE         Disable low threshold interrupt at y-axis
      @param channel_z
      @n     INTERRUPT_Z_ENABLE          Enable low threshold interrupt at z-axis
      @n     INTERRUPT_Z_DISABLE         Disable low threshold interrupt at z-axis
      @param low_threshold              Low threshold, default to expand 16 times, for example: if the threshold is set to be 1, actually the geomagnetic data below 16 will trigger an interrupt
      @param polarity
      @n     POLARITY_HIGH                   High polarity
      @n     POLARITY_LOW                    Low polarity
    '''
    if low_threshold < 0:
      self.__txbuf[0] = (low_threshold*-1) | 0x80
    else:
      self.__txbuf[0] = low_threshold
    self.write_reg(self.REG_LOW_THRESHOLD ,self.__txbuf)
    rslt = self.read_reg(self.REG_INT_CONFIG, 1)
    if channel_x == self.INTERRUPT_X_DISABLE:
      self.__txbuf[0] = rslt[0] | 0x01
    else:
      self.__txbuf[0] = rslt[0] & 0xFE
    if channel_y == self.INTERRUPT_Y_DISABLE:
      self.__txbuf[0] = self.__txbuf[0] | 0x02
    else:
      self.__txbuf[0] = self.__txbuf[0] & 0xFC
    if channel_x == self.INTERRUPT_X_DISABLE:
      self.__txbuf[0] = self.__txbuf[0] | 0x04
    else:
      self.__txbuf[0] = self.__txbuf[0] & 0xFB
    self.write_reg(self.REG_INT_CONFIG ,self.__txbuf)
    self.set_interrupt_pin(self.ENABLE_INTERRUPT_PIN, polarity)

  
  def get_low_threshold_interrupt_state(self):
    '''!
      @brief Get the status of low threshold interrupt, which axis triggered the low threshold interrupt
      @return status The returned number indicate the low threshold interrupt occur at which axis
      @n   bit0 is 1 indicate the interrupt occur at x-axis
      @n   bit1 is 1 indicate the interrupt occur at y-axis
      @n   bit2 is 1 indicate the interrupt occur at z-axis
      @n     ------------------------------------
      @n     | bit7 ~ bit3 | bit2 | bit1 | bit0 |
      @n     ------------------------------------
      @n     |  reserved   |  0   |  0   |  0   |
      @n     ------------------------------------
    '''
    rslt = self.read_reg(self.REG_INTERRUPT_STATUS, 1)
    return rslt[0]&0x07

  def set_high_threshold_interrupt(self, channel_x, channel_y, channel_z, high_threshold, polarity):
    '''!
      @brief Set high threshold interrupt, an interrupt is triggered when the geomagnetic value of a channel is beyond the threshold, the threshold is default to expand 16 times
      @n    There will be level change when INT pin interrupt occurred
      @n    High pin polarity: active on high, the default is low level, which will jump when the threshold is triggered.
      @n    Low pin polarity: active on low, the default is high level, which will jump when the threshold is triggered.
      @param channel_x
      @n     INTERRUPT_X_ENABLE          Enable high threshold interrupt at x-axis
      @n     INTERRUPT_X_DISABLE         Disable high threshold interrupt at x-axis
      @param channel_y
      @n     INTERRUPT_Y_ENABLE          Enable high threshold interrupt at y-axis
      @n     INTERRUPT_Y_DISABLE         Disable high threshold interrupt at y-axis
      @param channel_z
      @n     INTERRUPT_Z_ENABLE          Enable high threshold interrupt at z-axis
      @n     INTERRUPT_Z_DISABLE         Disable high threshold interrupt at z-axis
      @param high_threshold              High threshold, default to expand 16 times, for example: if the threshold is set to be 1, actually the geomagnetic data beyond 16 will trigger an interrupt
      @param polarity
      @n     POLARITY_HIGH                   High polarity
      @n     POLARITY_LOW                    Low polarity
    '''
    if high_threshold < 0:
      self.__txbuf[0] = (high_threshold*-1) | 0x80
    else:
      self.__txbuf[0] = high_threshold
    self.write_reg(self.REG_HIGH_THRESHOLD, self.__txbuf)
    rslt = self.read_reg(self.REG_INT_CONFIG, 1)
    if channel_x == self.HIGH_INTERRUPT_X_DISABLE:
      self.__txbuf[0] = rslt[0] | 0x08
    else:
      self.__txbuf[0] = rslt[0] & 0xF7
    if channel_y == self.HIGH_INTERRUPT_Y_DISABLE:
      self.__txbuf[0] = self.__txbuf[0] | 0x10
    else:
      self.__txbuf[0] = self.__txbuf[0] & 0xEF
    if channel_x == self.HIGH_INTERRUPT_X_DISABLE:
      self.__txbuf[0] = self.__txbuf[0] | 0x20
    else:
      self.__txbuf[0] = self.__txbuf[0] & 0xDf    
    
    self.write_reg(self.REG_INT_CONFIG ,self.__txbuf)
    self.set_interrupt_pin(self.ENABLE_INTERRUPT_PIN, polarity)

  def get_high_threshold_interrupt_state(self):
    '''!
      @brief Get the status of high threshold interrupt, which axis triggered the high threshold interrupt
      @return status  The returned number indicate the high threshold interrupt occur at which axis
      @n bit0 is 1 indicate the interrupt occur at x-axis
      @n bit1 is 1 indicate the interrupt occur at y-axis
      @n bit2 is 1 indicate the interrupt occur at z-axis
      @n   ------------------------------------
      @n   | bit7 ~ bit3 | bit2 | bit1 | bit0 |
      @n   ------------------------------------
      @n   |  reserved   |  0   |  0   |  0   |
      @n   ------------------------------------
    '''
    rslt = self.read_reg(self.REG_INTERRUPT_STATUS, 1)
    return (rslt[0]&0x38)>>3

 
class bmm150_I2C(bmm150): 
     
     
  '''!
    @brief An example of an i2c interface module
  '''
    #I2C_BUS         = 0x01   #default use I2C1
    # I2C address select, that CS and SDO pin select 1 or 0 indicates the high or low level respectively. There are 4 combinations: 
  ADDRESS_0       = 0x10   # (CSB:0 SDO:0)
  ADDRESS_1       = 0x11   # (CSB:0 SDO:1)
  ADDRESS_2       = 0x12   # (CSB:1 SDO:0)
  ADDRESS_3       = 0x13   # (CSB:1 SDO:1) default i2c address
  
  def __init__(self, addr=ADDRESS_3, sdaPin=0, sclPin=1, retries=5, delay=1):
        from machine import Pin, SoftI2C
        
        self.__addr = addr
        self.sdaPin = sdaPin
        self.sclPin = sclPin
        self.retries = retries
        self.delay = delay
        
        # Tentatives de connexion avec des retries
        for attempt in range(self.retries):
            try:
                # Initialiser le bus I2C
                self.i2cbus = SoftI2C(scl=Pin(self.sclPin), sda=Pin(self.sdaPin), freq=100000)
                
                # Vérifier si le périphérique est présent
                devices = self.i2cbus.scan()
                if self.__addr not in devices:
                    raise OSError(f"BMM150 not found at address 0x{self.__addr:02X}")
                
                # Initialisation des paramètres
                self.set_power_bit(bmm150.ENABLE_POWER)
                utime.sleep_ms(100)  # Attendre la stabilisation
                
                self.set_operation_mode(bmm150.POWERMODE_NORMAL)
                self.set_preset_mode(bmm150.PRESETMODE_HIGHACCURACY)
                self.set_rate(bmm150.RATE_10HZ)
                self.set_measurement_xyz()

                #print("bmm150 : Périphérique détecté et initialisé avec succès!")
                break  # Si ça réussit, on sort de la boucle
            except OSError as e:
                #print(f"bmm150 : Tentative {attempt + 1} échouée: {e}")
                if attempt < self.retries - 1:  # Si ce n'est pas la dernière tentative
                    utime.sleep(self.delay)  # Attendre un peu avant de réessayer
                else:
                    print("bmm150 : Échec après plusieurs tentatives.")
                    raise  # Relancer l'exception si les tentatives échouent

    
  def write_reg(self, reg, data):
    '''!
      @brief writes data to a register
      @param reg register address
      @param data written data
    '''
    if isinstance(data, int):
        self.i2cbus.writeto_mem(self.__addr, reg, data.to_bytes(1,'little'))
    else:
        for i in data:
            self.i2cbus.writeto_mem(self.__addr, reg, i.to_bytes(1,'little'))
  
  def read_reg(self, reg ,len):
    '''!
      @brief read the data from the register
      @param reg register address
      @param len read data length
    '''
    if len == 1:
        return list(self.i2cbus.readfrom_mem(self.__addr, reg,1))
    else:
        return list(self.i2cbus.readfrom_mem(self.__addr, reg, len))
