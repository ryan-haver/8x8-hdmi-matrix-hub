package.preload['avswitch.avswitch_proxy_commands'] = (function (...)
--[[=============================================================================
    ReceivedFromProxy Code for the AVSwitch Proxy

    Copyright 2015 Control4 Corporation. All Rights Reserved.
===============================================================================]]

-- This macro is utilized to identify the version string of the driver template version used.
if (TEMPLATE_VERSION ~= nil) then
	TEMPLATE_VERSION.properties = "2015.03.31"
end

--=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
-- Power Functions
--=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
--[[
function PRX_CMD.ON(idBinding, tParams)
	--Handled by CONNECT_OUTPUT
	--gAVSwitchProxy:prx_ON(tParams)
end

function PRX_CMD.OFF(idBinding, tParams)
	--Handled by DISCONNECT_OUTPUT
	--gAVSwitchProxy:prx_OFF(tParams)
end
--]]

function PRX_CMD.CONNECT_OUTPUT(idBinding, tParams)
	gAVSwitchProxy:prx_CONNECT_OUTPUT(tParams)
end

function PRX_CMD.DISCONNECT_OUTPUT(idBinding, tParams)
	gAVSwitchProxy:prx_DISCONNECT_OUTPUT(tParams)
end

--=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
-- Input Selection and AV Path Functions
--=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
function PRX_CMD.SET_INPUT(idBinding, tParams)
	gAVSwitchProxy:prx_SET_INPUT(idBinding, tParams)
end

function PRX_CMD.BINDING_CHANGE_ACTION(idBinding, tParams)
	gAVSwitchProxy:prx_BINDING_CHANGE_ACTION(idBinding, tParams)
end

function PRX_CMD.IS_AV_OUTPUT_TO_INPUT_VALID(idBinding, tParams)
	return gAVSwitchProxy:prx_IS_AV_OUTPUT_TO_INPUT_VALID(idBinding, tParams)
end

--=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
-- Volume Control Functions
--=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
function PRX_CMD.MUTE_OFF(idBinding, tParams)
	gAVSwitchProxy:prx_MUTE_OFF(tParams)
end

function PRX_CMD.MUTE_ON(idBinding, tParams)
	gAVSwitchProxy:prx_MUTE_ON(tParams)	
end

function PRX_CMD.MUTE_TOGGLE(idBinding, tParams)
	gAVSwitchProxy:prx_MUTE_TOGGLE(tParams)
end

function PRX_CMD.SET_VOLUME_LEVEL(idBinding, tParams)
	gAVSwitchProxy:prx_SET_VOLUME_LEVEL(tParams)
end

function PRX_CMD.PULSE_VOL_DOWN(idBinding, tParams)
	gAVSwitchProxy:prx_PULSE_VOL_DOWN(tParams)
end

function PRX_CMD.PULSE_VOL_UP(idBinding, tParams)
	gAVSwitchProxy:prx_PULSE_VOL_UP(tParams)
end

function PRX_CMD.START_VOL_DOWN(idBinding, tParams)
	gAVSwitchProxy:prx_START_VOL_DOWN(tParams)
end

function PRX_CMD.START_VOL_UP(idBinding, tParams)
	gAVSwitchProxy:prx_START_VOL_UP(tParams)
end

function PRX_CMD.STOP_VOL_DOWN(idBinding, tParams)
	gAVSwitchProxy:prx_STOP_VOL_DOWN(tParams)
end

function PRX_CMD.STOP_VOL_UP(idBinding, tParams)
	gAVSwitchProxy:prx_STOP_VOL_UP(tParams)
end

function PRX_CMD.PULSE_BASS_DOWN(idBinding, tParams)
	gAVSwitchProxy:prx_PULSE_BASS_DOWN(tParams)
end

function PRX_CMD.PULSE_BASS_UP(idBinding, tParams)
	gAVSwitchProxy:prx_PULSE_BASS_UP(tParams)
end

function PRX_CMD.SET_BASS_LEVEL(idBinding, tParams)
	gAVSwitchProxy:prx_SET_BASS_LEVEL(tParams)
end

function PRX_CMD.PULSE_TREBLE_DOWN(idBinding, tParams)
	gAVSwitchProxy:prx_PULSE_TREBLE_DOWN(tParams)
end

function PRX_CMD.PULSE_TREBLE_UP(idBinding, tParams)
	gAVSwitchProxy:prx_PULSE_TREBLE_UP(tParams)
end

function PRX_CMD.SET_TREBLE_LEVEL(idBinding, tParams)
	gAVSwitchProxy:prx_SET_TREBLE_LEVEL(tParams)
end

--=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
-- Menu Functions
--=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
function PRX_CMD.INFO(idBinding, tParams)
	gAVSwitchProxy:prx_INFO(idBinding, tParams)
end

function PRX_CMD.GUIDE(idBinding, tParams)
	gAVSwitchProxy:prx_GUIDE(idBinding, tParams)
end

function PRX_CMD.MENU(idBinding, tParams)
	gAVSwitchProxy:prx_MENU(idBinding, tParams)
end

function PRX_CMD.CANCEL(idBinding, tParams)
	gAVSwitchProxy:prx_CANCEL(idBinding, tParams)
end

function PRX_CMD.UP(idBinding, tParams)
	gAVSwitchProxy:prx_UP(idBinding, tParams)
end

function PRX_CMD.DOWN(idBinding, tParams)
	gAVSwitchProxy:prx_DOWN(idBinding, tParams)
end

function PRX_CMD.LEFT(idBinding, tParams)
	gAVSwitchProxy:prx_LEFT(idBinding, tParams)
end

function PRX_CMD.START_DOWN(idBinding, tParams)
	gAVSwitchProxy:prx_START_DOWN(idBinding, tParams)
end

function PRX_CMD.START_UP(idBinding, tParams)
	gAVSwitchProxy:prx_START_UP(idBinding, tParams)
end

function PRX_CMD.START_LEFT(idBinding, tParams)
	gAVSwitchProxy:prx_START_LEFT(idBinding, tParams)
end

function PRX_CMD.START_RIGHT(idBinding, tParams)
	gAVSwitchProxy:prx_START_RIGHT(idBinding, tParams)
end

function PRX_CMD.STOP_DOWN(idBinding, tParams)
	gAVSwitchProxy:prx_STOP_DOWN(idBinding, tParams)
end

function PRX_CMD.STOP_UP(idBinding, tParams)
	gAVSwitchProxy:prx_STOP_UP(idBinding, tParams)
end

function PRX_CMD.STOP_LEFT(idBinding, tParams)
	gAVSwitchProxy:prx_STOP_LEFT(idBinding, tParams)
end

function PRX_CMD.STOP_RIGHT(idBinding, tParams)
	gAVSwitchProxy:prx_STOP_RIGHT(idBinding, tParams)
end

function PRX_CMD.RIGHT(idBinding, tParams)
	gAVSwitchProxy:prx_RIGHT(idBinding, tParams)
end

function PRX_CMD.ENTER(idBinding, tParams)
	gAVSwitchProxy:prx_ENTER(idBinding, tParams)
end

function PRX_CMD.RECALL(idBinding, tParams)
	gAVSwitchProxy:prx_RECALL(idBinding, tParams)
end

function PRX_CMD.OPEN_CLOSE(idBinding, tParams)
	gAVSwitchProxy:prx_OPEN_CLOSE(idBinding, tParams)
end

function PRX_CMD.PROGRAM_A(idBinding, tParams)
	gAVSwitchProxy:prx_PROGRAM_A(idBinding, tParams)
end

function PRX_CMD.PROGRAM_B(idBinding, tParams)
	gAVSwitchProxy:prx_PROGRAM_B(idBinding, tParams)
end

function PRX_CMD.PROGRAM_C(idBinding, tParams)
	gAVSwitchProxy:prx_PROGRAM_C(idBinding, tParams)
end

function PRX_CMD.PROGRAM_D(idBinding, tParams)
	gAVSwitchProxy:prx_PROGRAM_D(idBinding, tParams)
end

--=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
-- Digit Functions
--=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
function PRX_CMD.NUMBER_0(idBinding, tParams)
	gAVSwitchProxy:prx_NUMBER_0(idBinding, tParams)
end

function PRX_CMD.NUMBER_1(idBinding, tParams)
	gAVSwitchProxy:prx_NUMBER_1(idBinding, tParams)
end

function PRX_CMD.NUMBER_2(idBinding, tParams)
	gAVSwitchProxy:prx_NUMBER_2(idBinding, tParams)
end

function PRX_CMD.NUMBER_3(idBinding, tParams)
	gAVSwitchProxy:prx_NUMBER_3(idBinding, tParams)
end

function PRX_CMD.NUMBER_4(idBinding, tParams)
	gAVSwitchProxy:prx_NUMBER_4(idBinding, tParams)
end

function PRX_CMD.NUMBER_5(idBinding, tParams)
	gAVSwitchProxy:prx_NUMBER_5(idBinding, tParams)
end

function PRX_CMD.NUMBER_6(idBinding, tParams)
	gAVSwitchProxy:prx_NUMBER_6(idBinding, tParams)
end

function PRX_CMD.NUMBER_7(idBinding, tParams)
	gAVSwitchProxy:prx_NUMBER_7(idBinding, tParams)
end

function PRX_CMD.NUMBER_8(idBinding, tParams)
	gAVSwitchProxy:prx_NUMBER_8(idBinding, tParams)
end

function PRX_CMD.NUMBER_9(idBinding, tParams)
	gAVSwitchProxy:prx_NUMBER_9(idBinding, tParams)
end

function PRX_CMD.STAR(idBinding, tParams)
	gAVSwitchProxy:prx_STAR(idBinding, tParams)
end

function PRX_CMD.POUND(idBinding, tParams)
	gAVSwitchProxy:prx_POUND(idBinding, tParams)
end
 end)
package.preload['avswitch.avswitch_proxy_notifies'] = (function (...)
--[[=============================================================================
    Received Proxy Notification Code

    Copyright 2015 Control4 Corporation. All Rights Reserved.
===============================================================================]]

-- This macro is utilized to identify the version string of the driver template version used.
if (TEMPLATE_VERSION ~= nil) then
	TEMPLATE_VERSION.properties = "2015.03.31"
end

--[[
	Notify: INPUT_OUTPUT_CHANGED
	Sent to the proxy to indicate the currently selected Input has changed on the specified Output
	Parameters
		bindingID - proxy id of proxy bound to input connection
		input_id - value of Input Connection ID
		output_id - value of Output Connection ID
--]]
function NOTIFY.INPUT_OUTPUT_CHANGED(bindingID, input_id, output_id)
	local tParams = {}
	if (tonumber(output_id) >= 4000) then
		tParams = {INPUT = input_id, OUTPUT = output_id, AUDIO=true, VIDEO=false}
	else
		tParams = {INPUT = input_id, OUTPUT = output_id, AUDIO=false, VIDEO=true}
	end
    SendNotify("INPUT_OUTPUT_CHANGED", tParams, bindingID)
end
------------------------------ Power Notification Functions ------------------------------
function NOTIFY.ON()
	SendSimpleNotify("ON")
end

function NOTIFY.OFF()
	SendSimpleNotify("OFF")
end
------------------------------ Volume Notification Code ------------------------------
--[[
	Notify: VOLUME_LEVEL_CHANGED
	Sent to the AVSwitch proxy to indicate that the Volume level has changed on the specified Output
	Parameters
		bindingID - proxy id of AVSwitch proxy
		output - mod 1000 value of Output Connection ID
		level - C4 level uses a percentage scale: 0 - 100
--]]
function NOTIFY.VOLUME_LEVEL_CHANGED(bindingID, output, level)
    local tParams = {LEVEL = level, OUTPUT = output + 4000}
    SendNotify("VOLUME_LEVEL_CHANGED", tParams, bindingID)	
end

--[[
	Notify: BASS_LEVEL_CHANGED
	Sent to the AVSwitch proxy to indicate that the Bass level has changed on the specified Output
	Parameters
		bindingID - proxy id of AVSwitch proxy
		output - mod 1000 value of Output Connection ID
		level - C4 volume level uses a percentage scale: 0 - 100
--]]
function NOTIFY.BASS_LEVEL_CHANGED(bindingID, output, level)
    local tParams = {LEVEL = level, OUTPUT = output + 4000}
    SendNotify("BASS_LEVEL_CHANGED", tParams, bindingID)		
end

--[[
	Notify: TREBLE_LEVEL_CHANGED
	Sent to the AVSwitch proxy to indicate that the Treble level has changed on the specified Output
	Parameters
		bindingID - proxy id of AVSwitch proxy
		output - mod 1000 value of Output Connection ID
		level - C4 volume level uses a percentage scale: 0 - 100
--]]
function NOTIFY.TREBLE_LEVEL_CHANGED(bindingID, output, level)
    local tParams = {LEVEL = level, OUTPUT = output + 4000}
    SendNotify("TREBLE_LEVEL_CHANGED", tParams, bindingID)	
end

--[[
	Notify: BALANCE_LEVEL_CHANGED
	Sent to the AVSwitch proxy to indicate that the Balance level has changed on the specified Output
	Parameters
		bindingID - proxy id of AVSwitch proxy
		output - mod 1000 value of Output Connection ID
		level - C4 volume level uses a percentage scale: 0 - 100
--]]
function NOTIFY.BALANCE_LEVEL_CHANGED(bindingID, output, level)
    local tParams = {LEVEL = level, OUTPUT = output + 4000}
    SendNotify("BALANCE_LEVEL_CHANGED", tParams, bindingID)		
end

--[[
	Notify: LOUNDENSS_CHANGED
	Sent to the AVSwitch proxy to indicate that the Loudness state has changed on the specified Output
	Parameters
		bindingID - proxy id of AVSwitch proxy
		output - mod 1000 value of Output Connection ID
		state - represented as "True" or "False" (literal string, not boolean)
--]]
function NOTIFY.LOUDNESS_CHANGED(bindingID, output, state)
    local tParams = {LOUDNESS = state, OUTPUT = output + 4000}
    SendNotify("LOUDNESS_CHANGED", tParams, bindingID)		
end

--[[
	Notify: MUTE_LEVEL_CHANGED
	Sent to the AVSwitch proxy to indicate that the Mute state has changed on the specified Output
	Parameters
		bindingID - proxy id of AVSwitch proxy
		output - mod 1000 value of Output Connection ID
		state - represented as "True" or "False" (literal string, not boolean)
--]]
function NOTIFY.MUTE_CHANGED(bindingID, output, state)
    local tParams = {MUTE = state, OUTPUT = output + 4000}
    SendNotify("MUTE_CHANGED", tParams, bindingID)		
end
	 end)
package.preload['common.c4_command'] = (function (...)
--[[=============================================================================
    Functions for handling and executing commands and actions

    Copyright 2016 Control4 Corporation. All Rights Reserved.
===============================================================================]]
require "common.c4_driver_declarations"

-- Set template version for this file
if (TEMPLATE_VERSION ~= nil) then
	TEMPLATE_VERSION.c4_command = "2016.01.08"
end

--[[=============================================================================
    ExecuteCommand(sCommand, tParams)

    Description
    Function called by Director when a command is received for this DriverWorks
    driver. This includes commands created in Composer programming.

    Parameters
    sCommand(string) - Command to be sent
    tParams(table)   - Lua table of parameters for the sent command

    Returns
    Nothing
===============================================================================]]
function ExecuteCommand(sCommand, tParams)
	LogTrace("ExecuteCommand(" .. sCommand .. ")")
	LogInfo(tParams)

	-- Remove any spaces (trim the command)
	local trimmedCommand = string.gsub(sCommand, " ", "")
	local status, ret

	-- if function exists then execute (non-stripped)
	if (EX_CMD[sCommand] ~= nil and type(EX_CMD[sCommand]) == "function") then
		status, ret = pcall(EX_CMD[sCommand], tParams)
	-- elseif trimmed function exists then execute
	elseif (EX_CMD[trimmedCommand] ~= nil and type(EX_CMD[trimmedCommand]) == "function") then
		status, ret = pcall(EX_CMD[trimmedCommand], tParams)
	elseif (EX_CMD[sCommand] ~= nil) then
		QueueCommand(EX_CMD[sCommand])
		status = true
	else
		LogInfo("ExecuteCommand: Unhandled command = " .. sCommand)
		status = true
	end
	
	if (not status) then
		LogError("LUA_ERROR: " .. ret)
	end
	
	return ret -- Return whatever the function returns because it might be xml, a return code, and so on
end

--[[=============================================================================
    EX_CMD.LUA_ACTION(tParams)

    Description
    Function called for any actions executed by the user from the Actions Tab
    in Composer.

    Parameters
    tParams(table) - Lua table of parameters for the command option

    Returns
    Nothing
===============================================================================]]
function EX_CMD.LUA_ACTION(tParams)
	if (tParams ~= nil) then
		for cmd, cmdv in pairs(tParams) do
			if (cmd == "ACTION" and cmdv ~= nil) then
				local status, err = pcall(LUA_ACTION[cmdv], tParams)
				if (not status) then
					LogError("LUA_ERROR: " .. err)
				end
				break
			end
		end
	end
end

--[[=============================================================================
    ReceivedFromProxy(idBinding, sCommand, tParams)

    Description
    Function called for any actions executed by the user from the Actions Tab
    in Composer.

    Parameters
    idBinding(int)   - Binding ID of the proxy that sent a BindMessage to the
                       DriverWorks driver.
    sCommand(string) - Command that was sent
    tParams(table)   - Lua table of received command parameters

    Returns
    Nothing
===============================================================================]]
function ReceivedFromProxy(idBinding, sCommand, tParams)

	if (sCommand ~= nil) then

		-- initial table variable if nil
		if (tParams == nil) then
			tParams = {}
		end
		
		LogTrace("ReceivedFromProxy(): " .. sCommand .. " on binding " .. idBinding .. "; Call Function PRX_CMD." .. sCommand .. "()")
		LogInfo(tParams)

		if ((PRX_CMD[sCommand]) ~= nil) then
			local status, err = pcall(PRX_CMD[sCommand], idBinding, tParams)
			if (not status) then
				LogError("LUA_ERROR: " .. err)
			end
		else
			LogInfo("ReceivedFromProxy: Unhandled command = " .. sCommand)
		end
	end
end

--[[
	This function is called when a UI (Navigator) requests data, and
	calls the function requested.
--]]
function UIRequest(sRequest, tParams)
	local ret = ""

	if (sRequest ~= nil) then
		tParams = tParams or {}   -- initial table variable if nil
		LogTrace("UIRequest(): " .. sRequest .. "; Call Function UI_REQ." .. sRequest .. "()")
		LogInfo(tParams)

		if (UI_REQ[sRequest]) ~= nil then
			ret = UI_REQ[sRequest](tParams)
		else
			LogWarn("UIRequest: Unhandled request = " .. sRequest)
		end
	end

	return ret
end
 end)
package.preload['common.c4_common'] = (function (...)
--[[=============================================================================
    ON_INIT, Timer,s and Property management functions

    Copyright 2016 Control4 Corporation. All Rights Reserved.
===============================================================================]]
require "common.c4_driver_declarations"
require "lib.c4_log"
require "lib.c4_timer"

-- Set template version for this file
if (TEMPLATE_VERSION ~= nil) then
	TEMPLATE_VERSION.c4_common = "2016.01.08"
end

--[[=============================================================================
    Create and Initialize Logging
===============================================================================]]
function ON_DRIVER_EARLY_INIT.c4_common()
	-- Create a logger
	LOG = c4_log:new("Template_c4z Change Name")
end

function ON_DRIVER_INIT.c4_common()
	-- Create Log Timer
	gC4LogTimer = c4_timer:new("Log Timer", 45, "MINUTES", OnLogTimerExpired)
end

--[[=============================================================================
    Log timer callback function
===============================================================================]]
function OnLogTimerExpired()
	LogWarn("Turning Log Mode Off (timer expired)")
	gC4LogTimer:KillTimer()
	
	C4:UpdateProperty("Log Mode", "Off")
	OnPropertyChanged("Log Mode")
end

gForceLogging = false
function ON_PROPERTY_CHANGED.LogMode(propertyValue)
	gC4LogTimer:KillTimer()
	
	if (gForceLogging) then
		LOG:OutputPrint(true)
		LOG:OutputC4Log(true)
	else
		LOG:OutputPrint(propertyValue:find("Print") ~= nil)
		LOG:OutputC4Log(propertyValue:find("Log") ~= nil)
		if (propertyValue == "Off") then
			return
		end
		
		gC4LogTimer:StartTimer()
	end
end

function ON_PROPERTY_CHANGED.LogLevel(propertyValue)
	if (gForceLogging) then
		LOG:SetLogLevel("5 - Debug")
	else
		LOG:SetLogLevel(propertyValue)
	end
end

--[[=============================================================================
    Print Template Versions
===============================================================================]]
function TemplateVersion()
	print ("\nTemplate Versions")
	print ("-----------------------")
	for k, v in pairs(TEMPLATE_VERSION) do
		print (k .. " = " .. v)
	end
	
	print ("")
end end)
package.preload['common.c4_conditional'] = (function (...)
--[[=============================================================================
    Functions for handling conditionals in control4 project programming

    Copyright 2017 Control4 Corporation. All Rights Reserved.
===============================================================================]]

require "common.c4_driver_declarations"

-- Set template version for this file
if (TEMPLATE_VERSION ~= nil) then
	TEMPLATE_VERSION.c4_conditional = "2017.04.25"
end

function TestCondition(ConditionalName, tParams)
	LogTrace("TestCondition() : %s", tostring(ConditionalName))
--	LOG:Trace(tParams)
	
	local retVal = false
	local callSuccess = false
	local trimmedConditionalName = string.gsub(ConditionalName, " ", "")

	if (PROG_CONDITIONAL[ConditionalName] ~= nil and type(PROG_CONDITIONAL[ConditionalName]) == "function") then
		callSuccess, retVal = pcall(PROG_CONDITIONAL[ConditionalName], tParams)

		-- elseif trimmed function exists then execute
	elseif (PROG_CONDITIONAL[trimmedConditionalName] ~= nil and type(PROG_CONDITIONAL[trimmedConditionalName]) == "function") then
		callSuccess, retVal = pcall(PROG_CONDITIONAL[trimmedConditionalName], tParams)

	else
		LogInfo("TestCondition: Unhandled condition = %s", tostring(ConditionalName))
	end
	
	if (not callSuccess) then
		LogError("LUA_ERROR: %s", tostring(retVal))
	end

	LogTrace("Result = " .. tostring(retVal))
	return retVal
end

 end)
package.preload['common.c4_device_connection_base'] = (function (...)
--[[=============================================================================
    DeviceConnectionBase Class

    Copyright 2016 Control4 Corporation. All Rights Reserved.
===============================================================================]]
require "common.c4_common"
require "lib.c4_object"
require "lib.c4_log"
require "lib.c4_timer"
require "lib.c4_queue"

-- Set template version for this file
if (TEMPLATE_VERSION ~= nil) then
	TEMPLATE_VERSION.c4_device_connection_base = "2016.01.08"
end

COMMAND_QUEUE_SIZE = 100
DEFAULT_COMMAND_DELAY_INTERVAL = 100            -- Don't send consecutive commands faster than this many milliseconds
DEFAULT_COMMAND_RESPONSE_INTERVAL = 3           -- If we haven't received and ACK after this many seconds, try again
DEFAULT_RETRY_COUNT_MAX = 3

function ON_DRIVER_EARLY_INIT.c4_device_connection_base()
	gReceiveBuffer = ""
	gIsUrlConnected = false
	gIsNetworkServerConnected = false
	gIsNetworkConnected = false
	gIsSerialConnected = false
	gIsIRConnected = false
end

DeviceConnectionBase = inheritsFrom(nil)

function DeviceConnectionBase:construct()

	self._IsConnected = false
	self._SendTimer = nil
	self._WaitResponseTimer = nil
	self._CommandQueue = nil
	self._Priority1CommandQueue = nil
	self._Priority2CommandQueue = nil
	self._LastCommand = nil
	self._ExpectAck = false
	self._CommandRetryCount = 0
	self._RetryCountMax = DEFAULT_RETRY_COUNT_MAX

	self._SendCommandDelayMS = DEFAULT_COMMAND_DELAY_INTERVAL
	self._CommandResponseWaitS = DEFAULT_COMMAND_RESPONSE_INTERVAL
	
	-- Polling
	self._PollingInterval = 0
	self._PollingUnits = "SECONDS"
	self._PollingTimer = nil
end

function DeviceConnectionBase:Initialize(ExpectAck, CommandDelayInterval, CommandResponseInterval, CallbackParam)

	if (ExpectAck ~= nil) then
		self._ExpectAck = ExpectAck
	end

	if (CommandDelayInterval ~= nil) then
		self._SendCommandDelayMS = CommandDelayInterval
	end

	if (CommandResponseInterval ~= nil) then
		self._CommandResponseWaitS = CommandResponseInterval
	end

	self._CommandQueue = c4_queue:new()
	self._CommandQueue:SetMaxSize(COMMAND_QUEUE_SIZE)
	self._CommandQueue:SetName("Command Queue")

	self._Priority1CommandQueue = c4_queue:new()
	self._Priority1CommandQueue:SetMaxSize(COMMAND_QUEUE_SIZE)
	self._Priority1CommandQueue:SetName("P1 Queue")

	self._Priority2CommandQueue = c4_queue:new()
	self._Priority2CommandQueue:SetMaxSize(COMMAND_QUEUE_SIZE)
	self._Priority2CommandQueue:SetName("P2 Queue")

	-- usually only one of these timers will be used, but it's pretty low overhead to instantiate both of them
	self._SendTimer = c4_timer:new("SendCommand", self._SendCommandDelayMS, "MILLISECONDS", DeviceConnectionBase.OnSendTimeExpired, false, CallbackParam)
	self._WaitResponseTimer = c4_timer:new("WaitResponse", self._CommandResponseWaitS, "SECONDS", DeviceConnectionBase.OnWaitTimeExpired, false, CallbackParam)
end

function DeviceConnectionBase:InitPolling(PollingInterval, PollingUnits, CallbackParam)
	LogFatal("DeviceConnectionBase:InitPolling()")
	if (PollingInterval ~= nil) then
		self._PollingInterval = PollingInterval
	end
	
	self._PollingUnits = PollingUnits or self._PollingUnits

	LogFatal("self._PollingInterval: %s, self._PollingUnits: %s", tostring(self._PollingInterval), tostring(self._PollingUnits))
	
	-- create polling timer
	self._PollingTimer = c4_timer:new("Polling", self._PollingInterval, self._PollingUnits, DeviceConnectionBase.OnPollingTimerExpired, false, CallbackParam)
end

function DeviceConnectionBase:StartPolling(interval, units)
	LogFatal("DeviceConnectionBase:StartPolling()")
	LogFatal("self._PollingTimer: %s", tostring(self._PollingTimer))
	
	if (self._PollingTimer ~= nil) then
		self._PollingTimer:KillTimer()
		
		local timer_units = units or self._PollingTimer._units
		local timer_interval = interval or self._PollingInterval

		self._PollingTimer:StartTimer(timer_interval, timer_units)
	end
end

function DeviceConnectionBase:StopPolling()
	LogFatal("DeviceConnectionBase:StopPolling()")
	self._PollingTimer:KillTimer()
end

function DeviceConnectionBase:SetExpectACK(ExpectACK)
	self._ExpectAck = ExpectACK
end

function DeviceConnectionBase:SetCommandDelayInterval(DelayInterval)
	self._SendCommandDelayMS = DelayInterval
end

function DeviceConnectionBase:SetResponseWaitInterval(WaitInterval)
	self._CommandResponseWaitS = WaitInterval
end

function DeviceConnectionBase:ReceivedFromCom(sData)

	gReceiveBuffer = gReceiveBuffer .. sData
	LogTrace("ReceivedFromCom  ReceiveBuffer is now {{{%s}}}", gReceiveBuffer)

	message = self:GetMessage()
	while (message ~= nil and message ~= "") do
		status, err = pcall(HandleMessage, message)
		if (status) then
			message = self:GetMessage()
		else
			LogError("LUA_ERROR: " .. err)
			message = ""
			gReceiveBuffer = ""
		end
	end
end

function DeviceConnectionBase:SetConnection(IsConnected, method)
	self._IsConnected = IsConnected
	gControlMethod = method
end

function DeviceConnectionBase:ControlMethod()
	-- Override in derived class
	print("WARNING: Need to override ControlMethod - should never be called")
	
	return ""
end

function DeviceConnectionBase:StartCommandTimer(...)
	local value = select(1, ...)
	local units = select(2, ...)
	local command_name = select(3, ...) or ""

	self._WaitResponseTimer:KillTimer()
	self._SendTimer:KillTimer()

	if (self._ExpectAck) then
		-- expecting an ACK set the Response Wait timer
		local timer_units = units or self._WaitResponseTimer._units
		local timer_interval = value or self._CommandResponseWaitS

		self._WaitResponseTimer:StartTimer(timer_interval, timer_units)
		LogTrace(string.format("Starting wait Timer:  %d", self._WaitResponseTimer._timerID) .. " for " .. command_name)
	else
		-- no ACK expected, just wait the designated amount of time and send another command
		local timer_units = units or self._SendTimer._units
		local timer_interval = value or self._SendCommandDelayMS

		self._SendTimer:StartTimer(timer_interval, timer_units)
		LogTrace(string.format("Starting Send Timer:  %d for %s (timer_interval = %d, timer_units = %s)", self._SendTimer._timerID, command_name, timer_interval, timer_units))
	end
end

-- Note the '.' instead of the ':'
function DeviceConnectionBase.OnSendTimeExpired(Instance)
	LogTrace("Send Timer expired")
	Instance._SendTimer:KillTimer()

	local tCommand = Instance._LastCommand
	if (tCommand ~= nil) then
		if (tCommand.command_name ~= nil) then
			LogTrace("Send Timer expired - Last Command: %s, Send Next Command", tostring(tCommand.command_name))
		elseif (type(tCommand) == "string") then
			LogTrace("Send Timer expired - Last Command: %s, Send Next Command", tostring(tCommand))
		end
	else
		LogTrace("Send Timer expired - Last Command: UNKNOWN, Send Next Command")
	end
	
	Instance._LastCommand = nil
	Instance:SendNextCommand()

	if (DoEvents ~= nil and type(DoEvents) == "function") then
		DoEvents()
	end
end

function DeviceConnectionBase.OnWaitTimeExpired(Instance)
	LogTrace("Wait Timer expired")
	Instance._WaitResponseTimer:KillTimer()
	Instance._CommandRetryCount = Instance._CommandRetryCount + 1

	if (Instance._CommandRetryCount >= Instance._RetryCountMax) then
		-- To many retries, pop the current command and try the next one
		Instance._CommandRetryCount = 0
		Instance:SendNextCommand()
	else
		Instance:SendLastCommand()
	end
end

function DeviceConnectionBase.OnPollingTimerExpired(Instance)
	LogTrace("Polling Timer expired")
	Instance._PollingTimer:KillTimer()

	OnPollingTimerExpired()
	
	Instance._PollingTimer:StartTimer(Instance._PollingInterval)
end

function DeviceConnectionBase:HandleACK()
	self._LastCommand = nil
	
	self._WaitResponseTimer:KillTimer()
	self._CommandRetryCount = 0
	self:SendNextCommand()
end

function DeviceConnectionBase:QueueEmpty()
	return (self._CommandQueue:empty() and self._Priority1CommandQueue:empty() and self._Priority2CommandQueue:empty())
end

function DeviceConnectionBase:QueueCommand(sCommand, ...)
--	LogTrace("QueueCommand(%s)", sCommand)
	local command_delay = select(1, ...)
	local delay_units = select(2, ...)
	local command_name = select(3, ...)

	if (sCommand == nil) or (sCommand == "") then
		return
	end

	if (self._LastCommand == nil) then
		self._CommandQueue:push(sCommand, command_delay, delay_units, command_name)
		self._LastCommand = self._CommandQueue:pop()
		self:SendCommand(sCommand, command_delay, delay_units, command_name)
	else
		self._CommandQueue:push(sCommand, command_delay, delay_units, command_name)
	end
end

function DeviceConnectionBase:QueuePriority1Command(sCommand, ...)
	LogTrace("QueuePriority1Command(%s)", sCommand)
	local command_delay = select(1, ...)
	local delay_units = select(2, ...)
	local command_name = select(3, ...)

	if (sCommand == nil) or (sCommand == "") then
		return
	end

	if (self._LastCommand == nil) then
		self._Priority1CommandQueue:push(sCommand, command_delay, delay_units, command_name)
		self._LastCommand = self._Priority1CommandQueue:pop()
		self:SendCommand(sCommand, command_delay, delay_units, command_name)
	else
		self._Priority1CommandQueue:push(sCommand, command_delay, delay_units, command_name)
	end
end

function DeviceConnectionBase:QueuePriority2Command(sCommand, ...)
	LogTrace("QueuePriority2Command(%s)", sCommand)
	local command_delay = select(1, ...)
	local delay_units = select(2, ...)
	local command_name = select(3, ...)

	if (sCommand == nil) or (sCommand == "") then
		return
	end

	if (self._LastCommand == nil) then
		self._Priority2CommandQueue:push(sCommand, command_delay, delay_units, command_name)
		self._LastCommand = self._Priority2CommandQueue:pop()
		self:SendCommand(sCommand, command_delay, delay_units, command_name)
	else
		self._Priority2CommandQueue:push(sCommand, command_delay, delay_units, command_name)
	end
end

function DeviceConnectionBase:SendNextCommand()
	LogTrace("DeviceConnectionBase:SendNextCommand")

	local tCommand = nil
	if (not self._Priority1CommandQueue:empty()) then
		tCommand = self._Priority1CommandQueue:pop()
		LogTrace(tostring(gCon._Priority1CommandQueue))
	elseif (not self._Priority2CommandQueue:empty()) then
		tCommand = self._Priority2CommandQueue:pop()
		LogTrace(tostring(gCon._Priority2CommandQueue))
	elseif (not self._CommandQueue:empty()) then
		tCommand = self._CommandQueue:pop()
		LogTrace(tostring(gCon._CommandQueue))
	end
	
	if (tCommand ~= nil) then
		self._LastCommand = tCommand
		local sCommand = tCommand.command
		local command_delay = tCommand.command_delay
		local delay_units = tCommand.delay_units
		local command_name = tCommand.command_name

		if (sCommand == nil or sCommand == "") then
			self._SendTimer:KillTimer()
			self._WaitResponseTimer:KillTimer()
		else
			LogTrace("SendCommand: %s", sCommand)
			self:SendCommand(sCommand, command_delay, delay_units, command_name)
		end
	end
end

function DeviceConnectionBase:SendLastCommand()
--	LogTrace("DeviceConnectionBase:SendLastCommand")

	local tCommand = self._LastCommand
	if (tCommand ~= nil) then
		local sCommand = tCommand.command
		local command_delay = tCommand.command_delay
		local delay_units = tCommand.delay_units
		local command_name = tCommand.command_name

		if (sCommand == nil or sCommand == "") then
			self._SendTimer:KillTimer()
			self._WaitResponseTimer:KillTimer()
		else
			LogTrace("SendCommand: %s", sCommand)
			self:SendCommand(sCommand, command_delay, delay_units, command_name)
		end
	end
end

function DeviceConnectionBase:SendCommand()
	-- Dummy routine.  Override in derived class
	print("Need to override SendCommand - should never be called")
end


function DeviceConnectionBase:GetMessage()
	
	-- Brain dead version of this routine. Just return the current receive buffer.
	-- It's very likely that a GetMessage() function will need to be created
	if (GetMessage ~= nil and type(GetMessage) == "function") then
		return GetMessage()
	else
		local ComMessage = gReceiveBuffer
		gReceiveBuffer = ""

		return ComMessage
	end
end

--[[=============================================================================
    Other Connection Functions
===============================================================================]]

function ReceivedFromSerial(idBinding, sData)
	if (gCon.ReceivedFromSerial == nil) then return end --serial is bound but not the current control method
	gCon:ReceivedFromSerial(idBinding, sData)
end

function ReceivedFromNetwork(idBinding, nPort, sData)
	gCon:ReceivedFromNetwork(idBinding, nPort, sData)
end

function OnServerDataIn(nHandle, strData)
--	LogTrace("Received Data on Handle: " .. nHandle .. ": " .. strData)
--	LogTrace("Data Is: %s", HexToString(strData))
	gCon:ReceivedFromNetworkServer(nHandle, strData)
end


--[[=============================================================================
    The ReceivedAsync function is called in response to 'url_get_request'. 
    The ticketId is the number returned from the request.
===============================================================================]]
function ReceivedAsync(ticketId, strData, responseCode, tHeaders)
	strData = strData or ""
	responseCode = responseCode or 0
	tHeaders = tHeaders or {}

--	LogTrace("ReceivedAsync[" .. ticketId .. "]: Response Code: " .. responseCode .. " Length: " .. string.len(strData))
--	LogTrace(tHeaders)

	gCon:ReceivedAsync(ticketId, strData, responseCode, tHeaders)
end
	
--[[=============================================================================
    OnBindingChanged(idBinding, class, bIsBound)
  
    Description:
    Function called by Director when a binding changes state(bound or unbound).
  
    Parameters:
    idBinding(int) - ID of the binding whose state has changed.
    class(string)  - Class of binding that has changed.
                     A single binding can have multiple classes(i.e. COMPONENT,
                     STEREO, RS_232, etc).
                     This indicates which has been bound or unbound.
    bIsBound(bool) - Whether the binding has been bound or unbound.
  
    Returns:
    None
===============================================================================]]
function OnBindingChanged(idBinding, class, bIsBound)
	
	LogTrace("OnBindingChanged(): idBinding = " .. tostring(idBinding) .. ", class = " .. class .. ", bIsBound = " .. tostring(bIsBound))
	if (idBinding == SERIAL_BINDING_ID) then
		gIsSerialConnected = bIsBound
		SetControlMethod()
		OnSerialConnectionChanged(idBinding, class, bIsBound)
	elseif (idBinding == IR_BINDING_ID) then
		gIsIRConnected = bIsBound
		SetControlMethod()
		OnIRConnectionChanged(idBinding, class, bIsBound)
	elseif(OnConnectionChanged ~= nil and type(OnConnectionChanged) == "function") then
		OnConnectionChanged(idBinding, class, bIsBound)
	end
end

--[[=============================================================================
    OnNetworkBindingChanged(idBinding, bIsBound)
  
    Description:
    Function called by Director when a network binding changes state(bound or unbound).
  
    Parameters:
    idBinding(int) - ID of the binding whose state has changed.
    bIsBound(bool) - Whether the binding has been bound or unbound.
  
    Returns:
    None
===============================================================================]]
function OnNetworkBindingChanged(idBinding, bIsBound)
	LogTrace('OnNetworkBindingChanged(): idBinding = ' .. tostring(idBinding) .. ' bIsBound = ' .. tostring(bIsBound))

	gIsNetworkConnected = bIsBound
	SetControlMethod()
	OnNetworkConnectionChanged(idBinding, bIsBound)
	if (bIsBound) then
		-- Start a special instance of reconnect timer to eventually do NetConnect if not done automatically
		gCon._NetworkReconnectTimer:StartTimer(gNetworkReconnectInterval) 	
	end	
end

--[[=============================================================================
    OnConnectionStatusChanged(idBinding, nPort, sStatus)
  
    Description:
    Sets the updated status of the specified binding
  
    Parameters:
    idBinding(int)  - ID of the binding whose status has changed
    nPort(int)      - The communication port of the specified bindings connection
    sStatus(string) - "ONLINE" if the connection status is to be set to Online,
                      any other value will set the status to Offline
  
    Returns:
    None
===============================================================================]]
function OnConnectionStatusChanged(idBinding, nPort, sStatus)
	LogTrace("OnConnectionStatusChanged[" .. idBinding .. " (" .. tostring(nPort) .. ")]: " .. sStatus)

	local isOnline = false

	gNetworkStatus = sStatus	
	if (sStatus == "ONLINE") then
		isOnline = true
	end

	gCon:SetOnlineStatus(isOnline)
	OnNetworkStatusChanged(idBinding, nPort, sStatus)
end

--[[=============================================================================
    SetControlMethod()
  
    Description:
    Sets the control method type for the drivers internal infrastructure
  
    Parameters:
    None
  
    Returns:
    The type of control method for the drivers connection(i.e. Network, Serial,
    IR, or (none))
===============================================================================]]
function SetControlMethod()
	if (gCon ~= nil) then
		if (gIsNetworkConnected == false) and (gCon._NetworkReconnectTimer ~= nil) then
			--housekeeping when changing from network control to serial or IR control
			gCon._NetworkReconnectTimer:KillTimer() 
		end
	end


	if( gIsNetworkServerConnected) then
		-- connect to NetworkServer communicator if not already connected
		if (gCon == nil or gCon.ControlMethod() ~= "NetworkServer") then
			gCon = NetworkServerConnectionBase:new()
			gCon:Initialize()
		end
		gCon:SetConnection(true, "NetworkServer")
	elseif (gIsNetworkConnected) then
		-- connect to Network communicator if not already connected
		if (gCon == nil or gCon.ControlMethod() ~= "Network") then
			gCon = NetworkConnectionBase:new(NETWORK_BINDING_ID, NETWORK_PORT)
			gCon:Initialize(COM_USE_ACK, COM_COMMAND_DELAY_MILLISECONDS, COM_COMMAND_RESPONSE_TIMEOUT_SECONDS)
		end
		gCon:SetConnection(true, "Network")
	elseif (gIsUrlConnected) then
		-- connect to URL communicator if not already connected
		if (gCon == nil or gCon.ControlMethod() ~= "URL") then
			gCon = UrlConnectionBase:new()
			gCon:Initialize(COM_USE_ACK, COM_COMMAND_DELAY_MILLISECONDS, COM_COMMAND_RESPONSE_TIMEOUT_SECONDS)
		end
		gCon:SetConnection(true, "URL")
	elseif (gIsSerialConnected) then
		-- connect to Serial communicator if not already connected
		if (gCon == nil or gCon.ControlMethod() ~= "Serial") then
			gCon = SerialConnectionBase:new(SERIAL_BINDING_ID)
			gCon:Initialize(COM_USE_ACK, COM_COMMAND_DELAY_MILLISECONDS, COM_COMMAND_RESPONSE_TIMEOUT_SECONDS)
			gCon:InitPolling(tonumber(gPollingTimerInterval), "MINUTES", gCon)
		end
		gCon:SetConnection(true, "Serial")
	elseif (gIsIRConnected) then
		-- connect to IR communicator if not already connected
		if (gCon == nil or gCon.ControlMethod() ~= "IR") then
			gCon = IRConnectionBase:new(IR_BINDING_ID)
			gCon:Initialize(COM_USE_ACK, COM_COMMAND_DELAY_MILLISECONDS, COM_COMMAND_RESPONSE_TIMEOUT_SECONDS)
		end
		gCon:SetConnection(true, "IR")
	else
		if (gCon ~= nil) then
			gCon:SetConnection(false, "(none)")
		end
		-- gCon = nil
	end

	gCon._CommandQueue:clear()
	gCon._Priority1CommandQueue:clear()
	gCon._Priority2CommandQueue:clear()
end

--[[=============================================================================
    ValidateControlMethod(controlMethod)
  
    Description:
    Identifies whether the specified control method has a valid connection
  
    Parameters:
    controlMethod(string) - The communication we are validating against
                            Valid types are (Network, Serial, and IR)
  
    Returns:
    true if the controlMethod specified has been connected, false otherwise.
===============================================================================]]
function ValidateControlMethod(controlMethod)
	local isValid = false

	if (controlMethod == "Network") and (gIsNetworkConnected) then
		isValid = true
	elseif (controlMethod == "URL") and (gIsUrlConnected) then
		isValid = true
	elseif (controlMethod == "Serial") and (gIsSerialConnected) then
		isValid = true
	elseif (controlMethod == "IR") and (gIsIRConnected) then
		isValid = true
	end

	return isValid
end
 end)
package.preload['common.c4_diagnostics'] = (function (...)
--[[=============================================================================
    Functions for Testing different aspects of the environment

    Copyright 2016 Control4 Corporation. All Rights Reserved.
===============================================================================]]
require "common.c4_driver_declarations"

-- Set template version for this file
if (TEMPLATE_VERSION ~= nil) then
	TEMPLATE_VERSION.c4_diagnostics = "2016.01.08"
end

function DisplayGlobals()

	print ("Global Variables")
	print ("----------------------------")
	for k,v in pairs(_G) do                             -- globals
		if not (type(v) == "function") then
			if (string.find(k, "^g%L")  == 1) then
				print(k .. ":  " .. tostring(v))
				if (type(v) == "table") then
					C4PrintTable(v, "   ")
				end
			end
		end
	end

	print ("")
end

function C4PrintTable(tValue, sIndent)

	sIndent = sIndent or "   "
	for k,v in pairs(tValue) do

		print(sIndent .. tostring(k) .. ":  " .. tostring(v))
		if (type(v) == "table") then
			C4PrintTable(v, sIndent .. "   ")
		end
	end
end end)
package.preload['common.c4_driver_declarations'] = (function (...)
--[[=============================================================================
    Driver Declarations used to call startup routines, teardown routines, and 
    other basic functions of the drivers operation

    Copyright 2017 Control4 Corporation. All Rights Reserved.
===============================================================================]]

-- Template Version Table
TEMPLATE_VERSION = {}
TEMPLATE_VERSION.c4_driver_declarations = "2017.04.25"

-- Command Handler Tables
EX_CMD = {}
PRX_CMD = {}
UI_REQ = {}
NOTIFY = {}
DEV_MSG = {}
LUA_ACTION = {}
PROG_CONDITIONAL = {}


--[[=============================================================================
    Tables of functions
    The following tables are function containers that are called within the
    following functions:

    OnDriverInit()
        First calls all functions contained within ON_DRIVER_EARLY_INIT table
        then calls all functions contained within ON_DRIVER_INIT table

    OnDriverLateInit()
        Calls all functions contained within ON_DRIVER_LATEINIT table

    OnDriverDestroyed()
        Calls all functions contained within ON_DRIVER_DESTROYED table

    OnPropertyChanged()
        Calls all functions contained within ON_PROPERTY_CHANGED table
===============================================================================]]
ON_DRIVER_INIT = {}
ON_DRIVER_EARLY_INIT = {}
ON_DRIVER_LATEINIT = {}
ON_DRIVER_DESTROYED = {}
ON_PROPERTY_CHANGED = {}

-- Constants
DEFAULT_PROXY_BINDINGID = 5001 end)
package.preload['common.c4_init'] = (function (...)
--[[=============================================================================
    Initial driver initialization and destruction functions

    Copyright 2016 Control4 Corporation. All Rights Reserved.
===============================================================================]]
require "common.c4_driver_declarations"
require "common.c4_property"

-- Set template version for this file
if (TEMPLATE_VERSION ~= nil) then
	TEMPLATE_VERSION.c4_init = "2016.01.08"
end

--[[=============================================================================
    OnDriverInit()

    Description
    Invoked by director when a driver is loaded. This API is provided for the
    driver developer to contain all of the driver objects that will require
    initialization.

    Parameters
    None

    Returns
    Nothing
===============================================================================]]
function OnDriverInit()
	gInitializingDriver = true
	C4:ErrorLog("INIT_CODE: OnDriverInit()")

	-- Call all ON_DRIVER_EARLY_INIT functions.
	for k,v in pairs(ON_DRIVER_EARLY_INIT) do
		if (ON_DRIVER_EARLY_INIT[k] ~= nil and type(ON_DRIVER_EARLY_INIT[k]) == "function") then
			C4:ErrorLog("INIT_CODE: ON_DRIVER_EARLY_INIT." .. k .. "()")
			local status, err = pcall(ON_DRIVER_EARLY_INIT[k])
			if (not status) then
				C4:ErrorLog("LUA_ERROR: " .. err)
			end
		end
	end

	-- Call all ON_DRIVER_INIT functions
	for k,v in pairs(ON_DRIVER_INIT) do
		if (ON_DRIVER_INIT[k] ~= nil and type(ON_DRIVER_INIT[k]) == "function") then
			C4:ErrorLog("INIT_CODE: ON_DRIVER_INIT." .. k .. "()")
			local status, err = pcall(ON_DRIVER_INIT[k])
			if (not status) then
				C4:ErrorLog("LUA_ERROR: " .. err)
			end
		end
	end

	-- Fire OnPropertyChanged to set the initial Headers and other Property
	-- global sets, they'll change if Property is changed.
	for k,v in pairs(Properties) do
		C4:ErrorLog("INIT_CODE: Calling OnPropertyChanged - " .. k .. ": " .. v)
		local status, err = pcall(OnPropertyChanged, k)
		if (not status) then
			C4:ErrorLog("LUA_ERROR: " .. err)
		end
	end

	gInitializingDriver = false
end

--[[=============================================================================
    OnDriverLateInit()

    Description
    Invoked by director after all drivers in the project have been loaded. This
    API is provided for the driver developer to contain all of the driver
    objects that will require initialization after all drivers in the project
    have been loaded.

    Parameters
    None

    Returns
    Nothing
===============================================================================]]
function OnDriverLateInit()
	C4:ErrorLog("INIT_CODE: OnDriverLateInit()")
	
	-- Call all ON_DRIVER_LATEINIT functions
	for k,v in pairs(ON_DRIVER_LATEINIT) do
		if (ON_DRIVER_LATEINIT[k] ~= nil and type(ON_DRIVER_LATEINIT[k]) == "function") then
			C4:ErrorLog("INIT_CODE: ON_DRIVER_LATEINIT." .. k .. "()")
			ON_DRIVER_LATEINIT[k]()
		end
	end
end


--[[=============================================================================
    OnDriverDestroyed()
    Function called by Director when a driver is removed. Release things this
    driver has allocated such as timers.

    Parameters
    None

    Returns
    Nothing
===============================================================================]]
function OnDriverDestroyed()
	C4:ErrorLog("INIT_CODE: OnDriverDestroyed()")
	
	-- Call all ON_DRIVER_DESTROYED functions
	for k, v in pairs(ON_DRIVER_DESTROYED) do
		if (ON_DRIVER_DESTROYED[k] ~= nil and type(ON_DRIVER_DESTROYED[k]) == "function") then
			C4:ErrorLog("INIT_CODE: ON_DRIVER_DESTROYED." .. k .. "()")
			ON_DRIVER_DESTROYED[k]()
		end
	end
end end)
package.preload['common.c4_ir_connection'] = (function (...)
--[[=============================================================================
    Base for an IR connection driver

    Copyright 2016 Control4 Corporation. All Rights Reserved.
===============================================================================]]
require "common.c4_driver_declarations"
require "common.c4_device_connection_base"
require "lib.c4_log"
require "common.c4_common"

-- Set template version for this file
if (TEMPLATE_VERSION ~= nil) then
	TEMPLATE_VERSION.c4_ir_connection = "2016.01.08"
end

IRConnectionBase = inheritsFrom(DeviceConnectionBase)

function IRConnectionBase:construct(BindingID)
	self.superClass():construct()
	self._BindingID = BindingID
end

function IRConnectionBase:Initialize(ExpectAck, DelayInterval, WaitInterval)
	print("tSerConBase:Initialize")
	gControlMethod = "IR"
	self:superClass():Initialize(ExpectAck, DelayInterval, WaitInterval, self)
end

function IRConnectionBase:ControlMethod()
	return "IR"
end

function IRConnectionBase:SendCommand(sCommand, ...)
	if(self._IsConnected) then
		local command_delay = select(1, ...)
		local delay_units = select(2, ...)
		local command_name = select(3, ...)

		C4:SendIR(self._BindingID, sCommand)
		self:StartCommandTimer(command_delay, delay_units, command_name)
	else
		LogWarn("IR connection is not bound. Command not sent.")
	end
end
 end)
package.preload['common.c4_networkserver_connection'] = (function (...)
--[[=============================================================================
    Base for a network server connection driver

    Copyright 2016 Control4 Corporation. All Rights Reserved.
===============================================================================]]
require "common.c4_device_connection_base"
require "lib.c4_log"

-- Set template version for this file
if (TEMPLATE_VERSION ~= nil) then
	TEMPLATE_VERSION.c4_networkserver_connection = "2016.01.08"
end

DEFAULT_POLLING_INTERVAL_SECONDS = 30

gNetworkKeepAliveInterval = DEFAULT_POLLING_INTERVAL_SECONDS

JK_NETWORK_BINDING_ID = 6001
JK_IP_ADDRESS = "192.168.0.169"
JK_PORT = 0x0C00


NetworkServerConnectionBase = inheritsFrom(DeviceConnectionBase)

function NetworkServerConnectionBase:construct()
	self.superClass():construct()

	self._Port = JK_PORT
	self._Handle = 0
end

function NetworkServerConnectionBase:Initialize(ExpectAck, DelayInterval, WaitInterval)
	print("NetworkServerConnectionBase:Initialize")
	gControlMethod = "NetworkServer"
	self:superClass():Initialize(ExpectAck, DelayInterval, WaitInterval, self)

end

function NetworkServerConnectionBase:ControlMethod()
	return "NetworkServer"
end

function NetworkServerConnectionBase:SendCommand(sCommand, ...)
	if(self._IsConnected) then
		if(self._IsOnline) then
			local command_delay = select(1, ...)
			local delay_units = select(2, ...)
			local command_name = select(3, ...)

			C4:SendToNetwork(self._BindingID, self._Port, sCommand)
			self:StartCommandTimer(command_delay, delay_units, command_name)
		else
			self:CheckNetworkConnectionStatus()
		end
	else
		LogWarn("Not connected to network. Command not sent.")
	end
end


function NetworkServerConnectionBase:SendRaw(sData)
--	LogTrace("Sending raw: %s", HexToString(sData))
	C4:ServerSend(self._Handle, sData, #sData)
end


function NetworkServerConnectionBase:ReceivedFromNetworkServer(nHandle, sData)
	self._Handle = nHandle
	self:ReceivedFromCom(sData)
end


function NetworkServerConnectionBase:StartListening()
	LogTrace("Creating Listener on Port %d", self._Port)
	C4:CreateServer(self._Port)
end


function NetworkServerConnectionBase:StopListening()
	LogTrace("Closing Listener on Port %d", self._Port)
	C4:DestroyServer()
end



-- function NetworkServerConnectionBase:CheckNetworkConnectionStatus()
	-- if (self._IsConnected and (not self._IsOnline)) then
		-- LogWarn("Network status is OFFLINE. Trying to reconnect to the device's Control port...")
		-- C4:NetDisconnect(self._BindingID, self._Port)
		-- C4:NetConnect(self._BindingID, self._Port)
	-- end
-- end

-- function NetworkServerConnectionBase.OnKeepAliveTimerExpired(Instance)
	-- Instance._LastCheckin = Instance._LastCheckin + 1

	-- if(Instance._LastCheckin > 2) then
		-- if(not Instance._IsOnline) then
			-- C4:NetDisconnect(Instance._BindingID, Instance._Port)
			-- C4:NetConnect(Instance._BindingID, Instance._Port)
		-- else
			-- C4:NetDisconnect(Instance._BindingID, Instance._Port)
			-- LogWarn("Failed to receive poll responses... Disconnecting...")
		-- end
	-- end

	-- if (SendKeepAlivePollingCommand ~= nil and type(SendKeepAlivePollingCommand) == "function") then
		-- SendKeepAlivePollingCommand()
	-- end

	-- Instance._KeepAliveTimer:StartTimer(gNetworkKeepAliveInterval)
-- end

-- function NetworkServerConnectionBase:SetOnlineStatus(IsOnline)
	-- self._IsOnline = IsOnline

	-- if(IsOnline) then
		-- self._KeepAliveTimer:StartTimer()
		-- self._LastCheckin = 0
		-- if (UpdateProperty ~= nil and type(UpdateProperty) == "function") then
			-- UpdateProperty("Connected To Network", "true")
		-- end

		-- self:SendNextCommand()
	-- else
		-- self._KeepAliveTimer:KillTimer()
		-- if (UpdateProperty ~= nil and type(UpdateProperty) == "function") then
			-- UpdateProperty("Connected To Network", "false")
		-- end
	-- end
-- end

 end)
package.preload['common.c4_network_connection'] = (function (...)
--[[=============================================================================
    Base for a network connection driver

    Copyright 2016 Control4 Corporation. All Rights Reserved.
===============================================================================]]
require "common.c4_device_connection_base"
require "lib.c4_log"

-- Set template version for this file
if (TEMPLATE_VERSION ~= nil) then
	TEMPLATE_VERSION.c4_network_connection = "2016.01.08"
end

DEFAULT_POLLING_INTERVAL_SECONDS = 30
DEFAULT_RECONNECT_INTERVAL_SECONDS = 5

gNetworkKeepAliveInterval = DEFAULT_POLLING_INTERVAL_SECONDS
gNetworkReconnectInterval = DEFAULT_RECONNECT_INTERVAL_SECONDS

NetworkConnectionBase = inheritsFrom(DeviceConnectionBase)

function NetworkConnectionBase:construct(BindingID, Port)
	self.superClass():construct()

	self._BindingID = BindingID
	self._Port = Port
	self._LastCheckin = 0
	self._IsOnline = false
	self._KeepAliveTimer = nil
end

function NetworkConnectionBase:Initialize(ExpectAck, DelayInterval, WaitInterval)
	print("NetConBase:Initialize")
	gControlMethod = "Network"
	self:superClass():Initialize(ExpectAck, DelayInterval, WaitInterval, self)
	self._KeepAliveTimer = c4_timer:new("PollingTimer", gNetworkKeepAliveInterval, "SECONDS", NetworkConnectionBase.OnKeepAliveTimerExpired, false, self)
	self._NetworkReconnectTimer = c4_timer:new("NetworkReconnectTimer", gNetworkReconnectInterval, "SECONDS", NetworkConnectionBase.OnNetworkReconnectTimerExpired, false, self)
end

function NetworkConnectionBase:ControlMethod()
	return "Network"
end

function NetworkConnectionBase:SendCommand(sCommand, ...)
	if(self._IsConnected) then
		if(self._IsOnline) then
			local command_delay = select(1, ...)
			local delay_units = select(2, ...)
			local command_name = select(3, ...)

			C4:SendToNetwork(self._BindingID, self._Port, sCommand)
			self:StartCommandTimer(command_delay, delay_units, command_name)
		else
			self:CheckNetworkConnectionStatus()
		end
	else
		LogWarn("Not connected to network. Command not sent.")
	end
end

function NetworkConnectionBase:ReceivedFromNetwork(idBinding, nPort, sData)
	self._LastCheckin = 0
	self:ReceivedFromCom(sData)
end

function NetworkConnectionBase:CheckNetworkConnectionStatus()
	if (self._IsConnected and (not self._IsOnline)) then
		LogWarn("Network status is OFFLINE. Trying to reconnect to the device's Control port...")
		C4:NetDisconnect(self._BindingID, self._Port)
		--C4:NetConnect(self._BindingID, self._Port)
		self._NetworkReconnectTimer:StartTimer(gNetworkReconnectInterval)
	end
end

function NetworkConnectionBase.OnKeepAliveTimerExpired(Instance)
	Instance._LastCheckin = Instance._LastCheckin + 1

	if(Instance._LastCheckin == 3) then
		LogWarn("Failed to receive poll responses... initiating network recovery mode...")
		C4:NetDisconnect(Instance._BindingID, Instance._Port)
		Instance._NetworkReconnectTimer:StartTimer(gNetworkReconnectInterval)
		return
	elseif(Instance._LastCheckin > 4) then	
		Instance._LastCheckin = 4
	end

	if (SendKeepAlivePollingCommand ~= nil and type(SendKeepAlivePollingCommand) == "function" and Instance._IsOnline) then
		SendKeepAlivePollingCommand()
	end

	Instance._KeepAliveTimer:StartTimer(gNetworkKeepAliveInterval)
end

function NetworkConnectionBase.OnNetworkReconnectTimerExpired(Instance)
	if (Instance._IsConnected) then
		LogWarn("OnNetworkReconnectTimerExpired: Attempting to reactivate network connection...")
		C4:NetDisconnect(Instance._BindingID, Instance._Port)
		C4:NetConnect(Instance._BindingID, Instance._Port)
		Instance._NetworkReconnectTimer:StartTimer(gNetworkReconnectInterval)
	else
		LogWarn("Cannot attempt to reactivate, the network connection is not bound")
	end
end

function NetworkConnectionBase:SetOnlineStatus(IsOnline)
	self._IsOnline = IsOnline

	if(IsOnline) then
		self._KeepAliveTimer:StartTimer(gNetworkKeepAliveInterval)
		self._NetworkReconnectTimer:KillTimer()
		self._LastCheckin = 0
		if (UpdateProperty ~= nil and type(UpdateProperty) == "function") then
			UpdateProperty("Connected To Network", "true")
		end

		self:SendNextCommand()
	else
		self._KeepAliveTimer:KillTimer()
		self._NetworkReconnectTimer:StartTimer(gNetworkReconnectInterval)
		if (UpdateProperty ~= nil and type(UpdateProperty) == "function") then
			UpdateProperty("Connected To Network", "false")
		end
	end
end

function ON_DRIVER_LATEINIT.c4_network_connection()
	-- Ensure existing connection is taken into consideration (useful on Driver Update)
	if (gIsNetworkConnected) then
		if (gCon ~= nil and gCon._BindingID ~= nil) then
			local tmp = C4:GetBindingAddress(gCon._BindingID)
			if (tmp ~= nil and string.len(tmp) > 0) then 
				OnNetworkBindingChanged(gCon._BindingID, true) 
			end
		end
	end
end
 end)
package.preload['common.c4_notify'] = (function (...)
--[[=============================================================================
    Notification Functions

    Copyright 2016 Control4 Corporation. All Rights Reserved.
===============================================================================]]
require "common.c4_driver_declarations"

-- Set template version for this file
if (TEMPLATE_VERSION ~= nil) then
	TEMPLATE_VERSION.c4_notify = "2016.01.08"
end

--[[=============================================================================
    SendNotify(notifyText, tParams, bindingID)

    Description
    Forwards a notification to the proxy with a list of parameters

    Parameters
    notifyText(string) - The function identifier for the proxy
    tParams(table)     - Table of key value pairs that hold the the parameters
                         and their values used in the proxy function
    bindingID(int)     - The requests binding id

    Returns
    Nothing
===============================================================================]]
function SendNotify(notifyText, tParams, bindingID)
	C4:SendToProxy(bindingID, notifyText, tParams, "NOTIFY")
end

--[[=============================================================================
    SendSimpleNotify(notifyText, ...)

    Description
    Forwards a notification to the proxy with no parameters

    Parameters
    notifyText(string) - The function identifier for the proxy
    bindingID(int)     - Optional parameter containing the requests binding id,
                         if not specified then the DEFAULT_PROXY_ID is given.

    Returns
    Nothing
===============================================================================]]
function SendSimpleNotify(notifyText, ...)
	bindingID = select(1, ...) or DEFAULT_PROXY_BINDINGID
	C4:SendToProxy(bindingID, notifyText, {}, "NOTIFY")
end end)
package.preload['common.c4_property'] = (function (...)
--[[=============================================================================
    Function for changing properties

    Copyright 2016 Control4 Corporation. All Rights Reserved.
===============================================================================]]
require "common.c4_driver_declarations"

-- Set template version for this file
if (TEMPLATE_VERSION ~= nil) then
	TEMPLATE_VERSION.c4_property = "2016.01.08"
end

--[[=============================================================================
    OnPropertyChanged(sProperty)

    Description
    Function called by Director when a property changes value. The value of the
    property that has changed can be found with: Properties[sName]. Note that
    OnPropertyChanged is not called when the Property has been changed by the
    driver calling the UpdateProperty command, only when the Property is changed
    by the user from the Properties Page. This function is called by Director
    when a property changes value.

    Parameters
    sProperty(string) - Name of property that has changed.

    Returns
    Nothing
===============================================================================]]
function OnPropertyChanged(sProperty)
	local propertyValue = Properties[sProperty]

	if (LOG ~= nil and type(LOG) == "table") then
		LogTrace("OnPropertyChanged(" .. sProperty .. ") changed to: " .. Properties[sProperty])
	end

	-- Remove any spaces (trim the property)
	local trimmedProperty = string.gsub(sProperty, " ", "")
	local status = true
	local err = ""

	if (ON_PROPERTY_CHANGED[sProperty] ~= nil and type(ON_PROPERTY_CHANGED[sProperty]) == "function") then
		status, err = pcall(ON_PROPERTY_CHANGED[sProperty], propertyValue)
	elseif (ON_PROPERTY_CHANGED[trimmedProperty] ~= nil and type(ON_PROPERTY_CHANGED[trimmedProperty]) == "function") then
		status, err = pcall(ON_PROPERTY_CHANGED[trimmedProperty], propertyValue)
	end

	if (not status) then
		LogError("LUA_ERROR: " .. err)
	end
end

--[[=============================================================================
    UpdateProperty(propertyName, propertyValue)
  
    Description:
    Sets the value of the given property in the driver
  
    Parameters:
    propertyName(string)  - The name of the property to change
    propertyValue(string) - The value of the property being changed
  
    Returns:
    None
===============================================================================]]
function UpdateProperty(propertyName, propertyValue)
	if (Properties[propertyName] ~= nil) then
		C4:UpdateProperty(propertyName, propertyValue)
	end
end
 end)
package.preload['common.c4_serial_connection'] = (function (...)
--[[=============================================================================
    Base for a serial connection driver

    Copyright 2016 Control4 Corporation. All Rights Reserved.
===============================================================================]]
require "common.c4_driver_declarations"
require "common.c4_device_connection_base"
require "lib.c4_log"
require "common.c4_common"

-- Set template version for this file
if (TEMPLATE_VERSION ~= nil) then
	TEMPLATE_VERSION.c4_serial_connection = "2016.01.08"
end

SerialConnectionBase = inheritsFrom(DeviceConnectionBase)

function SerialConnectionBase:construct(BindingID)
	self.superClass():construct()
	self._BindingID = BindingID
end

function SerialConnectionBase:Initialize(ExpectAck, DelayInterval, WaitInterval)
	gControlMethod = "Serial"
	self:superClass():Initialize(ExpectAck, DelayInterval, WaitInterval, self)
end

function SerialConnectionBase:ControlMethod()
	return "Serial"
end

function SerialConnectionBase:SendCommand(sCommand, ...)
	if(self._IsConnected) then
		local command_delay = select(1, ...)
		local delay_units = select(2, ...)
		local command_name = select(3, ...)

		C4:SendToSerial(self._BindingID, sCommand)
		self:StartCommandTimer(command_delay, delay_units, command_name)
	else
		LogWarn("Not connected to serial. Command not sent.")
	end
end

function SerialConnectionBase:SendRaw(sData)
	C4:SendToSerial(self._BindingID, sData)
end


function SerialConnectionBase:ReceivedFromSerial(idBinding, sData)
	self:ReceivedFromCom(sData)
end
 end)
package.preload['common.c4_url_connection'] = (function (...)
--[[=============================================================================
    Base for a url connection driver

    Copyright 2016 Control4 Corporation. All Rights Reserved.
===============================================================================]]
require "common.c4_device_connection_base"

-- Set template version for this file
if (TEMPLATE_VERSION ~= nil) then
	TEMPLATE_VERSION.c4_url_connection = "2016.01.08"
end

UrlConnectionBase = inheritsFrom(DeviceConnectionBase)

function UrlConnectionBase:construct(Url)
	self.superClass():construct()
	self._Url = Url
end

function UrlConnectionBase:Initialize(ExpectAck, DelayInterval, WaitInterval)
	gControlMethod = "URL"
	self:superClass():Initialize(ExpectAck, DelayInterval, WaitInterval, self)
	OnURLConnectionChanged()
end

function UrlConnectionBase:ControlMethod()
	return "URL"
end

function UrlConnectionBase:SetUrl(Url)
	self._Url = Url
end

function UrlConnectionBase:SendCommand(sCommand, sHeader, ignoreConnect)
	ignoreConnect = ignoreConnect or false

	local ticketId
	if(self._IsConnected or ignoreConnect) then
		if (sHeader ~= nil) then
			ticketId = C4:urlPost(self._Url, sCommand, sHeader)
		else
			ticketId = C4:urlPost(self._Url, sCommand)
		end
	else
		LogWarn("Not connected. Command not sent.")
	end
	
	return ticketId
end

function UrlConnectionBase:SendCommandUrl(sCommand, url, sHeader, ignoreConnect)
	ignoreConnect = ignoreConnect or false

	local ticketId
	if(self._IsConnected or ignoreConnect) then
		if (sHeader ~= nil) then
			ticketId = C4:urlPost(url, sCommand, sHeader)
		else
			ticketId = C4:urlPost(url, sCommand)
		end
	else
		LogWarn("Not connected. Command not sent.")
	end
	
	return ticketId
end

function UrlConnectionBase:UrlPost(sCommand, url, sHeader, ignoreConnect)
	ignoreConnect = ignoreConnect or false

	local ticketId
	if(self._IsConnected or ignoreConnect) then
		if (sHeader ~= nil) then
			ticketId = C4:urlPost(url, sCommand, sHeader)
		else
			ticketId = C4:urlPost(url, sCommand)
		end
	else
		LogWarn("Not connected. Command not sent.")
	end
	
	return ticketId
end

function UrlConnectionBase:UrlGet(url, sHeader, ignoreConnect)
	ignoreConnect = ignoreConnect or false

	local ticketId
	if(self._IsConnected or ignoreConnect) then
		if (sHeader ~= nil) then
			ticketId = C4:urlGet(url, sHeader)
		else
			ticketId = C4:urlGet(url)
		end
	else
		LogWarn("Not connected. Command not sent.")
	end
	
	return ticketId
end

function UrlConnectionBase:ReceivedAsync(ticketId, sData, responseCode, tHeaders)
	LogTrace("ReceivedAsync[" .. ticketId .. "]: Response Code: " .. responseCode .. " Length: " .. string.len(sData))
	LogTrace(tHeaders)
	local tMessage = {
		["ticketId"] = ticketId,
		["sData"] = sData,
		["responseCode"] = responseCode,
		["tHeaders"] = tHeaders
	}
	
	status, err = pcall(HandleMessage, tMessage)
	if (not status) then
		LogError("LUA_ERROR: " .. err)
	end
end

function ConnectURL()
	gIsUrlConnected = true
	SetControlMethod()
end

function DisconnectURL()
	gIsUrlConnected = false
	SetControlMethod()
end
 end)
package.preload['common.c4_utils'] = (function (...)
--[[=============================================================================
    Helper functions

    Copyright 2016 Control4 Corporation. All Rights Reserved.
===============================================================================]]

-- Set template version for this file
if (TEMPLATE_VERSION ~= nil) then
	TEMPLATE_VERSION.c4_utils = "2016.01.08"
end

--[[=============================================================================
    AsciiToBCD(InString)

    Description
    Convert an ascii string to a binary coded decimal. Each decimal digit is
    stored in one byte, with the lower four bits encoding the digit in BCD form.

    Parameters
    InString(string) - Ascii string that is to be converted into bcd

    Returns
    The binary coded decimal
===============================================================================]]
function AsciiToBCD(InString)
	local WorkVal = 0
	local RetValStr = ""
	local DoingHighNybble = false
	local WorkStr = ((#InString % 2) == 0) and (InString) or ("0" .. InString)	-- make sure length is an even number

	for CharCount = 1, #WorkStr do
		local NumVal = tonumber(WorkStr:sub(CharCount, CharCount))

		WorkVal = bit.lshift(WorkVal, 4) + NumVal
		if (DoingHighNybble) then
			RetValStr = RetValStr .. string.char(WorkVal)
			WorkVal = 0
		end

		DoingHighNybble = (not DoingHighNybble)
	end

	return RetValStr
end

--[[=============================================================================
    BCDToAscii(InByte)

    Description
    Convert an BCD string to an ascii string.

    Parameters
    InByte(string) - Binary coded decimal that is to be converted into ascii

    Returns
    The ascii string
===============================================================================]]
function BCDToAscii(InByte)
	return tostring(bit.rshift(InByte, 4)) .. tostring(bit.band(InByte, 0x0F))
end

--[[=============================================================================
    MakeXMLNode(Tag, Value)

    Description
    Create an Xml element

    Parameters
    Tag(string)   - The Xml elements name
    Value(string) - The Xml elements value

    Returns
    The xml element created for the specified value
===============================================================================]]
function MakeXMLNode(Tag, Value)
	return "<" .. Tag .. ">" .. Value .. "</" .. Tag .. ">"
end

--[[=============================================================================
    MakeXMLAttrNode(Tag, Value, Attribute, AttrValue)

    Description
    Create an Xml element with an attribute

    Parameters
    Tag(string)       - The Xml elements name
    Value(string)     - The Xml elements value
    Attribute(string) - The attribute to be added to the Xml element
    AttrValue(string) - The value of the attribute to be added

    Returns
    The xml element created for the specified value
===============================================================================]]
function MakeXMLAttrNode(Tag, Value, Attribute, AttrValue)
    return "<" .. Tag .. " " .. Attribute .. "=\"" .. AttrValue .. "\">" .. Value .. "</" .. Tag .. ">"
end

--[[=============================================================================
    StringFromUnicode(UnicodeString)

    Description
    Convert a unicode string

    Parameters
    UnicodeString(string) - The unicode string to be converted to ascii

    Returns
    The ascii representation of the unicode string
===============================================================================]]
function StringFromUnicode(UnicodeString)
	local RetVal = ""

	-- extract every other byte from the unicode string
	for Index = 2, #UnicodeString, 2 do
		RetVal = RetVal .. string.sub(UnicodeString, Index, Index)
	end

	return RetVal
end

--[[=============================================================================
    StringSplit(s)

    Description
    Splits a string into multiple strings at an optionally specified delimiter
	If the delimiter is not specified, it will defalt to the space character

    Parameters
    s(string) - The string that is to be split into several strings
	d(string) - The delimiter to split the string on

    Returns
    A table of strings containing all the seperate values in the given string
===============================================================================]]
function StringSplit(s, d)
	local delim = (d ~= nil) and d or " "
	local result = {}

	if s == nil or s == "" then
		return result
	end

	for match in (s..delim):gmatch("(.-)"..delim) do
		table.insert(result, match)
	end

	return result
end

--[[=============================================================================
    toboolean(s)

    Description
    Returns a boolean representation of the given value

    Parameters
    val input value, may be of different types

    Returns
    The value true or false based on the given value
		If the value is of type string the return true if the first letter is "T" or "t" or if the string is "1"
		If the value is of type number the return true if the value is non-zero
		If the value is already a boolean, just return it.
===============================================================================]]
function toboolean(val)
	local rval = false;

	if type(val) == "string" and (string.lower(val) == 'true' or val == "1") then
		rval = true
	elseif type(val) == "number" and val ~= 0 then
		rval =  true
	elseif type(val) == "boolean" then
		rval = val
	end

	return rval
end

--[[=============================================================================
    tointeger(s)

    Description
    Force a number or a string representation of a number to be an integer

    Parameters
    val - A number or a string representation of a number

    Returns
    The the rounded off integer value.
===============================================================================]]
function tointeger(val)
	local nval = tonumber(val)
	return (nval >= 0) and math.floor(nval + 0.5) or math.ceil(nval - 0.5)
end


--[[=============================================================================
    Go(to, err, ...)

    Description
    Call a function with the given arguments if it exists or report the error

    Parameters
    to(string)  - The string to evaluate the boolean representation from
    err(string) - The error to report if the function does not exist
    ...         - Additional optional parameters for the function specified by
                  the "to" parameter

    Returns
    Nothing
===============================================================================]]
function Go(to, err, ...)
	if (type(to) == "function") then
		return to(...)
	else
		LogTrace(err)
	end
end

--[[=============================================================================
    IsEmpty(str)

    Description
    Identifies if the string given is nil or empty

    Parameters
    str(string) - The string to evaluate for the empty condition

    Returns
    True if the given value is empty, false otherwise
===============================================================================]]
function IsEmpty(str)
	return str == nil or str == ""
end

--[[=============================================================================
    ReverseTable(a)

    Description
    Reverse table entries (key=value, value=key)

    Parameters
    a(table) - The table to reverse

    Returns
    new reversed table
===============================================================================]]
function ReverseTable(a)
	local b = {}
	for k,v in pairs(a) do b[v] = k end
	return b
end

function tonumber_loc(str, base)
  local s = str:gsub(",", ".") -- Assume US Locale decimal separator
  local num = tonumber(s, base)
  if (num == nil) then
    s = str:gsub("%.", ",") -- Non-US Locale decimal separator
    num = tonumber(s, base)
  end
  return num
end

--[[=============================================================================
    HexToString(InString)

    Description
    Converts a string of Hex characters to a readable string of ASCII characters

    Parameters
    InString(string) - The string to be converted

    Returns
    A string showing the hex bytes of the InString
===============================================================================]]
function HexToString(InString)
	local RetVal = ""

	for Index = 1, #InString do
		RetVal = RetVal .. string.format("%02X ", InString:byte(Index))
	end
	return RetVal
end


--[[=============================================================================
    StringToHex(InString)

    Description
    Converts a string of ASCII characters to as string with the actual Hex bytes in them.
	Basically an array of hex bytes.

    Parameters
    InString(string) - The string to be converted

    Returns
    A string of hex bytes (really an array of hex values) 
===============================================================================]]
function StringToHex(InString)
	local RetVal = ""

	for HexByteString in string.gfind(InString, "%x%x") do
		RetVal = RetVal .. string.char(tonumber(HexByteString, 16))
	end
	return RetVal
end

function RecordHistory(severity, eventType, category, subcategory, description)
	C4:RecordHistory(severity, eventType, category, subcategory, description)
end

function RecordCriticalHistory(eventType, category, subcategory, description)
	RecordHistory("Critical", eventType, category, subcategory, description)
end

function RecordWarningHistory(eventType, category, subcategory, description)
	RecordHistory("Warning", eventType, category, subcategory, description)
end

function RecordInfoHistory(eventType, category, subcategory, description)
	RecordHistory("Info", eventType, category, subcategory, description)
end


 end)
package.preload['lib.c4_log'] = (function (...)
--[[=============================================================================
    c4_log Class

    Copyright 2016 Control4 Corporation. All Rights Reserved.
===============================================================================]]
require "common.c4_driver_declarations"
require "lib.c4_object"

-- Set template version for this file
if (TEMPLATE_VERSION ~= nil) then
	TEMPLATE_VERSION.c4_log = "2016.01.08"
end

c4_log = inheritsFrom(nil)

function c4_log:construct(logName)
	self._logLevel = tonumber(string.sub(Properties['Log Level'] or "", 1, 1)) or 5
	self._outputPrint = Properties['Log Mode']:find("Print") ~= nil
	self._outputC4Log = Properties['Log Mode']:find("Log") ~= nil
	self._logName = logName or ""

	-- make sure Property is up to date (no harm if absent)
	C4:UpdateProperty("Log Level", Properties['Log Level'])
end

function c4_log:SetLogLevel(level)
	self._logLevel = tonumber(string.sub(level or "", 1, 1)) or self._logLevel
end

function c4_log:LogLevel()
	return self._logLevel
end

function c4_log:OutputPrint(value)
	self._outputPrint = value
end

function c4_log:OutputC4Log(value)
	self._outputC4Log = value
end

function c4_log:SetLogName(logName)

	if (logName == nil or logName == "") then
		logName = ""
	else
		logName = logName .. ": "
	end

	self._logName = logName
end

function c4_log:LogName()
	return self._logName
end

function c4_log:Enabled()
	return (self._outputPrint or self._outputC4Log)
end

function c4_log:PrintEnabled()
	return self._outputPrint
end

function c4_log:C4LogEnabled()
	return self._outputC4Log
end

function c4_log:CreateTableText(tValue, tableText)
	tableText = tableText or ""

	if (type(tValue) == "table") then

		tableText = tableText .. "{"
		for k, v in pairs(tValue) do

			-- add key
			if (type(k) == "number") then
				tableText = tableText .. "[" .. tostring(k) .. "]="
			elseif (type(k) == "string") then
				tableText = tableText .. k .. "="
			else
				print (tostring(k) .. ": " .. tostring (v))
			end

			-- add value
			if (type(v) == "number") then
				tableText = tableText .. tostring(v) .. ","
			elseif (type(v) == "string") then
				tableText = tableText .. "'" .. v .. "',"
			elseif (type(v) == "table") then
				tableText = c4_log:CreateTableText(v, tableText)
				tableText = tableText .. ","
			elseif (type(v) == "boolean") then
				tableText = tableText .. tostring(v) .. ","
			end
		end

		tableText = tableText .. "}"
	end

	return tableText
end

function InsertIndent(indentLevel)
	local indentStr = ""

	for i=1, indentLevel do
		indentStr = indentStr .. "\t"
	end

	return indentStr
end

function c4_log:CreateTableTextFormatted(tValue, tableText, indentLevel)
	tableText = tableText or ""
	indentLevel = indentLevel or 0

	if (type(tValue) == "table") then

		indentLevel = indentLevel + 1
		tableText = tableText .. "{\n"
		for k, v in pairs(tValue) do

			-- add key
			if (type(k) == "number") then
				tableText = tableText .. InsertIndent(indentLevel) .. "[" .. tostring(k) .. "]="
			elseif (type(k) == "string") then
				tableText = tableText .. InsertIndent(indentLevel) .. k .. "="
			else
				print (tostring(k) .. ": " .. tostring (v))
			end

			-- add value
			if (type(v) == "number") then
				tableText = tableText .. tostring(v) .. ",\n"
			elseif (type(v) == "string") then
				tableText = tableText .. "'" .. v .. "',\n"
			elseif (type(v) == "table") then
				tableText = c4_log:CreateTableTextFormatted(v, tableText, indentLevel)
				tableText = tableText .. ",\n"
			elseif (type(v) == "boolean") then
				tableText = tableText .. tostring(v) .. ",\n"
			end
		end

		indentLevel = indentLevel - 1
		tableText = tableText .. InsertIndent(indentLevel) .. "}"
	end

	return tableText
end

MAX_TABLE_LEVELS = 10
function c4_log:PrintTable(tValue, tableText, sIndent, level)
	tableText = tableText or ""
	level = level + 1
	
	if (level <= MAX_TABLE_LEVELS) then
		if (type(tValue) == "table") then
			for k,v in pairs(tValue) do
				if (tableText == "") then
					tableText = sIndent .. tostring(k) .. ":  " .. tostring(v)
					if (sIndent == ".   ") then sIndent = "    " end
				else
					tableText = tableText .. "\n" .. sIndent .. tostring(k) .. ":  " .. tostring(v)
				end
				if (type(v) == "table") then
					tableText = self:PrintTable(v, tableText, sIndent .. "   ", level)
				end
			end
		else
			tableText = tableText .. "\n" .. sIndent .. tostring(tValue)
		end
	end
	
	return tableText
end

function c4_log:LogTable(tValue, sIndent, level)
	level = level + 1
	
	if (level <= MAX_TABLE_LEVELS) then
		if (type(tValue) == "table") then
			for k,v in pairs(tValue) do
				C4:ErrorLog(self._logName .. sIndent .. tostring(k) .. ":  " .. tostring(v))
				if (type(v) == "table") then
					self:LogTable(v, sIndent .. "   ", level)
				end
			end
		else
			C4:ErrorLog(self._logName .. sIndent .. tValue)
		end
	end
end

function c4_log:Print(logLevel, sLogText)

	if (self._logLevel >= logLevel) then
		if (type(sLogText) == "table") then
			if (self._outputPrint) then
				print (self:PrintTable(sLogText, tableText, ".   ", 0))
			end

			if (self._outputC4Log) then
				self:LogTable(sLogText, "   ", 0)
			end

			return
		end

		if (self._outputPrint) then
			print (sLogText)
		end

		if (self._outputC4Log) then
			C4:ErrorLog(self._logName .. tostring(sLogText))
		end
	end
end

function c4_log:Fatal(sLogText, ...)
	self:LogOutput(0, sLogText, ...)
end

function c4_log:Error(sLogText, ...)
	self:LogOutput(1, sLogText, ...)
end

function c4_log:Warn(sLogText, ...)
	self:LogOutput(2, sLogText, ...)
end

function c4_log:Info(sLogText, ...)
	self:LogOutput(3, sLogText, ...)
end

function c4_log:Debug(sLogText, ...)
	self:LogOutput(4, sLogText, ...)
end

function c4_log:Trace(sLogText, ...)
	self:LogOutput(5, sLogText, ...)
end

function c4_log:LogOutput(level, sLogText, ...)
	if (LogEnabled()) then
		if (type(sLogText) == "string") then
			sLogText = string.format(sLogText, ...)
		end

		self:Print(level, sLogText)
	end
end

--[[=============================================================================
    c4_log wrapper functions
===============================================================================]]
function TryLog(level, sLogText, ...)
	LOG:LogOutput(level, sLogText, ...)
end

--[[=============================================================================
    SetLogLevel(level)

    Description: 
    Sets the desired log level to view

    Parameters:
    level(int) - The logging level to set the message to
                 0 = Fatal
                 1 = Error
                 2 = Warn
                 3 = Info
                 4 = Debug
                 5 = Trace

    Returns:
    None
===============================================================================]]
function SetLogLevel(level)
	LOG:SetLogLevel(level)
end

--[[=============================================================================
    LogLevel()

    Description: 
    Returns the currently set log level

    Parameters:
    None

    Returns:
    The current log level
        0 = Fatal
        1 = Error
        2 = Warn
        3 = Info
        4 = Debug
        5 = Trace
===============================================================================]]
function LogLevel()
	return LOG:LogLevel()
end

--[[=============================================================================
    OutputPrint(value)

    Description: 
    Specifies whether to output log messages or not

    Parameters:
    value(bool) - true to enable logging output, false otherwise

    Returns:
    None
===============================================================================]]
function OutputPrint(value)
	LOG:OutputPrint(value)
end

--[[=============================================================================
    OutputPrint(value)

    Description: 
    Specifies whether to output log messages to file or not

    Parameters:
    value(bool) - true to enable logging output, false otherwise

    Returns:
    None
===============================================================================]]
function OutputC4Log(value)
	LOG:OutputC4Log(value)
end

--[[=============================================================================
    SetLogName(logName)

    Description: 
    Sets the name of the log file where the messages will be written to

    Parameters:
    logName(string) - Sets the name of the log to write messages to

    Returns:
    None
===============================================================================]]
function SetLogName(logName)
	LOG:SetLogName(logName)
end

--[[=============================================================================
    LogName(logName)

    Description: 
    Gets the name of the log file where the messages will be written to

    Parameters:
    None

    Returns:
    The value of the log file that has been set
===============================================================================]]
function LogName()
	return LOG:LogName()
end

--[[=============================================================================
    LogEnabled()

    Description: 
    Identifies if logging or print has been enabled

    Parameters:
    None

    Returns:
    true if either logging or print has been enabled, false otherwise
===============================================================================]]
function LogEnabled()
	return LOG:Enabled()
end

--[[=============================================================================
    PrintEnabled()

    Description: 
    Gets the state of print output

    Parameters:
    None

    Returns:
    true if print has been enabled, false otherwise
===============================================================================]]
function PrintEnabled()
	return LOG:PrintEnabled()
end

--[[=============================================================================
    C4LogEnabled()

    Description: 
    Gets the state of logging

    Parameters:
    None

    Returns:
    true if logging has been enabled, false otherwise
===============================================================================]]
function C4LogEnabled()
	return LOG:C4LogEnabled()
end

--[[=============================================================================
    LogFatal(sLogText, ...)

    Description: 
    Formats and prints a series of characters and values to the enabled outputs
    when the set logging level is Fatal(0) or higher

    Parameters:
    sLogText(string) - Format control string
    ...              - Optional arguments which will replace all the format
                       specifiers contained in the format string

    Returns:
    None
===============================================================================]]
function LogFatal(sLogText, ...)
	local status, err = pcall(TryLog, 0, sLogText, ...)
	if (not status) then
		LOG:Print(1, "LUA_ERROR - LogFatal failed: " .. err)
	end
end

--[[=============================================================================
    LogError(sLogText, ...)

    Description: 
    Formats and prints a series of characters and values to the enabled outputs
    when the set logging level is Error(1) or higher

    Parameters:
    sLogText(string) - Format control string
    ...              - Optional arguments which will replace all the format
                       specifiers contained in the format string

    Returns:
    None
===============================================================================]]
function LogError(sLogText, ...)
	local status, err = pcall(TryLog, 1, sLogText, ...)
	if (not status) then
		LOG:Print(1, "LUA_ERROR - LogError failed: " .. err)
	end
end

--[[=============================================================================
    LogWarn(sLogText, ...)

    Description: 
    Formats and prints a series of characters and values to the enabled outputs
    when the set logging level is Warn(2) or higher

    Parameters:
    sLogText(string) - Format control string
    ...              - Optional arguments which will replace all the format
                       specifiers contained in the format string

    Returns:
    None
===============================================================================]]
function LogWarn(sLogText, ...)
	local status, err = pcall(TryLog, 2, sLogText, ...)
	if (not status) then
		LOG:Print(1, "LUA_ERROR - LogWarn failed: " .. err)
	end
end

--[[=============================================================================
    LogInfo(sLogText, ...)

    Description: 
    Formats and prints a series of characters and values to the enabled outputs
    when the set logging level is Info(3) or higher

    Parameters:
    sLogText(string) - Format control string
    ...              - Optional arguments which will replace all the format
                       specifiers contained in the format string

    Returns:
    None
===============================================================================]]
function LogInfo(sLogText, ...)
	local status, err = pcall(TryLog, 3, sLogText, ...)
	if (not status) then
		LOG:Print(1, "LUA_ERROR - LogInfo failed: " .. err)
	end
end

--[[=============================================================================
    LogDebug(sLogText, ...)

    Description: 
    Formats and prints a series of characters and values to the enabled outputs
    when the set logging level is Debug(4) or higher

    Parameters:
    sLogText(string) - Format control string
    ...              - Optional arguments which will replace all the format
                       specifiers contained in the format string

    Returns:
    None
===============================================================================]]
function LogDebug(sLogText, ...)
	local status, err = pcall(TryLog, 4, sLogText, ...)
	if (not status) then
		LOG:Print(1, "LUA_ERROR - LogDebug failed: " .. err)
	end
end

--[[=============================================================================
    LogTrace(sLogText, ...)

    Description: 
    Formats and prints a series of characters and values to the enabled outputs
    when the set logging level is Trace(5) or higher

    Parameters:
    sLogText(string) - Format control string
    ...              - Optional arguments which will replace all the format
                       specifiers contained in the format string

    Returns:
    None
===============================================================================]]
function LogTrace(sLogText, ...)
	local status, err = pcall(TryLog, 5, sLogText, ...)
	if (not status) then
		LOG:Print(1, "LUA_ERROR - LogTrace failed: " .. err)
	end
end

function dbgPrint(buf)
	if (LOG:PrintEnabled()) then
		print (buf)
	end
end

function dbgHexdump(buf)
	hexdump(buf, dbgPrint)
end

--[[=============================================================================
    c4_log unit tests
===============================================================================]]
function __test_c4_log()
	require "test.C4Virtual"
	
	local LOG = c4_log:new("test_c4_log")
	assert(LOG:LogName() == "test_c4_log", "_logName is not equal to 'test_c4_log' it is: " .. LOG:LogName())

	-- Test setting log level
	LOG:SetLogLevel("2 - Warning")
	assert(LOG:LogLevel() == 2, "_logLevel is not equal to '2' it is: " .. LOG:LogLevel())

	LOG:SetLogLevel(3)
	assert(LOG:LogLevel() == 3, "_logLevel is not equal to '3' it is: " .. LOG:LogLevel())

	-- Test enabling logs
	LOG:OutputPrint(false)
	assert(LOG:PrintEnabled() == false, "_outputPrint is not equal to 'false' it is: " .. tostring(LOG:PrintEnabled()))

	LOG:OutputC4Log(true)
	assert(LOG:C4LogEnabled() == true, "_outputC4Log is not equal to 'true' it is: " .. tostring(LOG:C4LogEnabled()))

	LOG:SetLogLevel(4)
	LogTrace("***** This is a test *****")
end

function __test_CreatTableText()
	local tTest = {}

	tTest[1] = {}
	tTest[2] = {}
	tTest[3] = 30
	tTest[4] = "Forty"
	
	LogTrace("----- tText -----")
	LogTrace(tTest)

	local tTest2 = { One = {},
					 Two = {},
					 Three = 30,
					 Four = "Forty" }
	LogTrace("----- tText2 -----")
	LogTrace(tTest2)
	
	local tTest3 = { [1] = {},
					 [2] = {},
					 [3] = 30,
					 [4] = "Forty" }
	LogTrace("----- tText3 -----")
	LogTrace(tTest3)

	local tTest4 = { [1] = {},
					 Two = {},
					 [3] = 30,
					 [4] = "Forty",
					 Five = "Fifty" }
	LogTrace("----- tText4 -----")
	LogTrace(tTest4)

	local tableText = LOG:CreateTableText(tTest4)
	LogTrace("----- tableText -----")
	LogTrace(tableText)
	
	--local tNew = {[1] = {},[3] = 30,[4] = 'Forty',Five = 'Fifty',Two = {},}
	--LogTrace(tNew)
end

function __TestCreateTableTextFormatted()
	require "test.C4Virtual"
	
	local LOG = c4_log:new("test_c4_log")
	local tButtons = {
		Name = 'heat',
		Attributes = {},
		ChildNodes = {
			[1] = {
				Name = 'button',
				Attributes = {},
				ChildNodes = {
					[1] = {
						Value = '51',
						Attributes = {},
						Name = 'id',
						ChildNodes = {},
					},
					[2] = {
						Value = 'Pool Heater',
						Attributes = {},
						Name = 'button_text',
						ChildNodes = {},
					},
					[3] = {
						Value = 'POOLHT',
						Attributes = {},
						Name = 'button_name',
						ChildNodes = {},
					},
				},
			},
			[2] = {
				Name = 'button',
				Attributes = {},
				ChildNodes = {
					[1] = {
						Value = '53',
						Attributes = {},
						Name = 'id',
						ChildNodes = {},
					},
					[2] = {
						Value = 'Spa Heater',
						Attributes = {},
						Name = 'button_text',
						ChildNodes = {},
					},
					[3] = {
						Value = 'SPAHT',
						Attributes = {},
						Name = 'button_name',
						ChildNodes = {},
					},
				},
			},
			[3] = {
				Name = 'button',
				Attributes = {},
				ChildNodes = {
					[1] = {
						Value = '54',
						Attributes = {},
						Name = 'id',
						ChildNodes = {},
					},
					[2] = {Value = 'Pool Solar Heater',
						Attributes = {},
						Name = 'button_text',
						ChildNodes = {}
					},
					[3] = {
						Value = 'SOLHT',
						Attributes = {},
						Name = 'button_name',
						ChildNodes = {},
					},
				}
			}
		}
	}

	print(LOG:CreateTableTextFormatted(tButtons))
end end)
package.preload['lib.c4_object'] = (function (...)
--[[=============================================================================
    c4_object Class

    Copyright 2016 Control4 Corporation. All Rights Reserved.
===============================================================================]]

-- Set template version for this file
if (TEMPLATE_VERSION ~= nil) then
	TEMPLATE_VERSION.c4_object = "2016.01.08"
end

function inheritsFrom( baseClass )
	local new_class = {}
	local class_mt = { __index = new_class }

	function new_class:create(...)
		local newinst = {}

		setmetatable( newinst, class_mt )

		-- Call the constructor when we create this class
		if newinst.construct then
			-- Allow returning a different obj than self. This allows for readonly tables etc...
			newinst = newinst:construct(...) or newinst
		end

		return newinst
	end

	if nil ~= baseClass then
		setmetatable( new_class, { __index = baseClass } )
	end

	--[[=============================================================================
	    Implementation of additional OO properties starts here 
	===============================================================================]]
	
	-- Return the class object of the instance
	function new_class:class()
		return new_class
	end

	--[[=============================================================================
	    Return the super class object of the instance. 

	    Note Calling methods on the base class itself will modify
	    the base table's static properties. In order to have call
	    the base class' methods and have them modify the current object
	    use super() or superAsSelf(). 
	===============================================================================]]
	function new_class:superClass()
		return baseClass
	end

	--[[=============================================================================
	    Returns a table that allows calling of the base class's method
	    while maintaining the objects state as the modified state of the base
	    class' methods. For example consider the following statements (order matters):

	    -- The child sees the parents property if the child hasn't overriden the property
	       obj:superClass().id = "parent"
	       obj.id == "parent" -- true

	    -- Setting the property on the child overrides (hides) the parents property
	       obj.id = "child"
	       obj.id == "child" -- true

	    -- The super() method pass
	       obj:super().id == "parent" -- true
	       obj:super().id = "child"
	       obj:super().id == "parent" -- still true
	       obj.id == "child" -- still true
	===============================================================================]]
	function new_class:super()
		local holder = {}

		holder.child = self
		holder.parent = baseClass

		local mt = {}
		mt.__index = function(table, index)
			if table.parent[index] then
				return table.parent[index]
			else 
				return table.child[index]
			end
		end

		-- Only set the new values to the child.
		mt.__newindex = function(table, key, value)
			table.child[key] = value
		end

		mt.__tostring = function(table)
			return tostring(table.child)
		end

		setmetatable(holder, mt)
		return holder
	end

	new_class.new = new_class.create

	--[[=============================================================================
	    Return true if the caller is an instance of theClass
	===============================================================================]]
	function new_class:isa( theClass )
		local b_isa = false
		local cur_class = new_class

		while ( nil ~= cur_class ) and ( false == b_isa ) do
			if cur_class == theClass then
				b_isa = true
			else
				cur_class = cur_class:superClass()
			end
		end

		return b_isa
	end

	return new_class
end

--[[=============================================================================
    Inheritance unit tests
===============================================================================]]
function __test_inheritance()
	local b = inheritsFrom(nil)

	b.construct = function(self, msg)
		self._msg = msg
	end

	local t = inheritsFrom(b)
	t.construct = function(self, msg)
		self:super():construct(msg)
	end

	t1 = t:new("t1")
	t2 = t:new("t2")
	assert(t1._msg == "t1", "t1 message is not equal to 't1' it''s: " .. t1._msg)
	assert(t2._msg == "t2", "t2 message is not equal to 't2' it''s: " .. t2._msg)    
	assert(tostring(t1:super()) ==  tostring(t1), "tostrings don't match");
	assert(t1:superClass() == b, "superClass and baseClass should be the same. They are not.")

	t1:superClass().id = "parent"
	assert(t1.id == "parent", "obect''s super class has invalid property value: ", t1.id)

	-- Setting the property on the child overrides (hides) the parents property
	t1.id = "child"
	assert(t1.id == "child", "object instance variable has invalid property value: " .. t1.id)

	-- The super() method maintains the self pointer to the child and not to the base
	assert(t1:super().id == "parent", "superAsSelf found invalid value for base class variable")
	t1:super().id = "child1"
	assert(t1:super().id == "parent", "Setting of instance variable hid base classes variable from itself");
	assert(t1.id == "child1", "Settings of instance variable did not change child instance variable")
end end)
package.preload['lib.c4_queue'] = (function (...)
--[[=============================================================================
    c4_queue Class

    Copyright 2016 Control4 Corporation. All Rights Reserved.
===============================================================================]]
require "common.c4_driver_declarations"
require "lib.c4_object"

-- Set template version for this file
if (TEMPLATE_VERSION ~= nil) then
	TEMPLATE_VERSION.c4_queue = "2016.01.08"
end

c4_queue = inheritsFrom(nil)

function c4_queue:construct()
	-- entry table
	self._et = {first = 0, last = -1}
	self._maxSize = 0	-- no size limit
	self._name = ""

	local mt = getmetatable(self)
	if (mt ~= nil) then
		mt.__tostring = self.__tostring
	end
end

function c4_queue:__tostring()
	local tOutputString = {}
	table.insert(tOutputString, "--- Queue ---")
	if (not IsEmpty(self._name)) then
		table.insert(tOutputString, "  name = " .. tostring(self._name))
	end
	table.insert(tOutputString, "  first = " .. tostring(self._et.first))
	table.insert(tOutputString, "  last = " .. tostring(self._et.last))
	table.insert(tOutputString, "  number in queue = " .. tostring(self._et.last - self._et.first + 1))
	table.insert(tOutputString, "  maximum size = " .. self._maxSize)
	table.insert(tOutputString, "  next value = " .. tostring(self:value()))
	return table.concat(tOutputString, "\n")
end


-- push a value on the queue
function c4_queue:push(value, ...)
	local numItems = self._et.last - self._et.first + 1

	if ((self._maxSize <= 0) or (numItems < self._maxSize) ) then
		local last = self._et.last + 1
		self._et.last = last
		
		local interval = select(1, ...)
		local units = select(2, ...)
		local command_name = select(3, ...)
		self._et[last] = {["command"] = value, ["command_delay"] = interval, ["delay_units"] = units, ["command_name"] = command_name}		
		--LogTrace ("Queue:push(), first = " .. tostring(self._et.first) .. ", last = " .. tostring(self._et.last) .. ", number in queue = " .. tostring(self._et.last - self._et.first + 1) .. ", value = " .. value)
	else
		-- if addToQueue == true then push value to queue
		if (self:OnMaxSizeReached()) then
			local last = self._et.last + 1
			self._et.last = last
			self._et[last] = {["command"] = value, ["command_delay"] = interval, ["delay_units"] = units, ["command_name"] = command_name}
			--LogTrace ("Queue:push(), first = " .. tostring(self._et.first) .. ", last = " .. tostring(self._et.last) .. ", number in queue = " .. tostring(self._et.last - self._et.first + 1) .. ", value = " .. value)
		end
	end
end

function c4_queue:OnMaxSizeReached()
	--LogTrace ("Max Size Reached - clear queue and push value to the queue (default).")
	local addToQueue = true

	self:clear()
	return (addToQueue)
end

-- pop a value from the queue
function c4_queue:pop()
	local first = self._et.first

	if first > self._et.last then
		--LogTrace("Queue:pop(), queue is empty")
		return ""
	end

	local value = self._et[first]
	self._et[first] = nil        -- to allow garbage collection
	self._et.first = first + 1
	--LogTrace ("Queue:pop(), first = " .. tostring(self._et.first) .. ", last = " .. tostring(self._et.last) .. ", number in queue = " .. tostring(self._et.last - self._et.first + 1) .. ", value = " .. value)

	return value
end

-- clear queue
function c4_queue:clear()
	local first = self._et.first

	if first > self._et.last then
		--LogTrace ("Queue:clear(), queue is empty")
		return ""
	end

	self._et = {first = 0, last = -1}
	--LogTrace ("Queue:clear(), first = " .. tostring(self._et.first) .. ", last = " .. tostring(self._et.last) .. ", number in queue = " .. tostring(self._et.last - self._et.first + 1))
	--LogTrace (self._et)
end

-- return value of first item
function c4_queue:value()
	local first = self._et.first

	if (first > self._et.last) then
		return ""
	else
		return self._et[first]
	end
end

-- return queue's maximum size
function c4_queue:MaxSize()
	return self._maxSize
end

-- return queue's maximum size
function c4_queue:SetMaxSize(size)
	self._maxSize = size
end

function c4_queue:SetName(name)
	self._name = name
end

-- return the queue's current size
function c4_queue:Size()
	return self._et.last - self._et.first + 1
end

-- is queue empty?
function c4_queue:empty()
	-- print ("self._et.first = " .. tostring(self._et.first) .. ", self._et.last = " .. tostring(self._et.last))
	if (self._et.first > self._et.last) then
		return true
	else
		return false
	end
end

--[[
    c4_queue unit tests
--]]
function __test_c4_queue()
	require "test.C4Virtual"
	require "lib.c4_log"

	local LOG = c4_log:new("test_c4_queue")
	LOG:SetLogLevel(5)
	LOG:OutputPrint(true)

	-- create an instance of the queue
	local c4Queue = c4_queue:new()

	c4Queue:SetMaxSize(3)
	assert(c4Queue:MaxSize() == 3, "_maxSize is not equal to '3' it is: " .. c4Queue:MaxSize())

	c4Queue:push("Item #1 in Queue")
	c4Queue:push("Item #2 in Queue")
	c4Queue:push("Item #3 in Queue")
	c4Queue:push("Item #4 in Queue")  -- this should cause OnMaxSizeReached() to be called and clear the queue
	assert(c4Queue:Size() == 1, "queue size is not equal to '1' it is: " .. c4Queue:Size())

	print (c4Queue)

	-- Test inheritance overriding OnMaxSizeReached
	-- Create a new class
	c4_queue_new = inheritsFrom(c4_queue)

	-- override construct()
	function c4_queue_new:construct()
		self.superClass():construct()  -- call base class
		self._maxSizeOption = 1

		local mt = getmetatable(self)
		if (mt ~= nil) then
			mt.__tostring = self.__tostring
		end
	end

	-- override OnMaxSizeReached()
	function c4_queue_new:OnMaxSizeReached()
		--Default: clear queue and push value to the queue. (No need to overload,

		-- Option 1: Do Nothing, new item is not added to queue
		if (self._maxSizeOption == 1) then
			
			LogInfo("Max Size Reached - do nothing, new item not added to queue (option 1)")
			return (false)
		-- Option 2: pop value, and push new value on queue
		elseif(self._maxSizeOption == 2) then
			LogInfo("Max Size Reached - pop value, and push new value on queue (option 2)")
			self:pop()
			return (true)
		-- Option 3: clear queue and DO NOT push new value onto queue
		elseif(self._maxSizeOption == 3) then
			LogInfo("Max Size Reached - clear queue and DO NOT push new value onto queue")
			self:clear()
			return (false)
		end
	end

	-- create an instance of the new queue
	local c4QueueNew = c4_queue_new:new()
	c4QueueNew:SetMaxSize(3)
	c4QueueNew:push("Item #1 in Queue")
	c4QueueNew:push("Item #2 in Queue")
	c4QueueNew:push("Item #3 in Queue")
	c4QueueNew:push("Item #4 in Queue")  -- this should cause OnMaxSizeReached() to be called and clear the queue
	assert(c4QueueNew:Size() == 3, "queue size is not equal to '3' it is: " .. c4QueueNew:Size())

	print(c4QueueNew)
	print ("done...")
end end)
package.preload['lib.c4_timer'] = (function (...)
--[[=============================================================================
    c4_timer Class

    Copyright 2017 Control4 Corporation. All Rights Reserved.
===============================================================================]]
require "common.c4_driver_declarations"
require "lib.c4_object"

-- Set template version for this file
if (TEMPLATE_VERSION ~= nil) then
	TEMPLATE_VERSION.c4_timer = "2017.05.03"
end

c4_timer = inheritsFrom(nil)

function c4_timer:construct(name, interval, units, Callback, repeating, CallbackParam)
	self._name = name
	self._timerID = TimerLibGetNextTimerID()
	self._interval = interval
	self._units = units
	self._repeating = repeating or false
	self._Callback = Callback
	self._CallbackParam = CallbackParam or ""
	self._id = 0

	gTimerLibTimers[self._timerID] = self
	if (LOG ~= nil and type(LOG) == "table") then
		LogTrace("Created timer " .. self._name)
	end
end

function c4_timer:StartTimer(...)
	c4_timer:KillTimer()

	-- optional parameters (interval, units, repeating)
	if ... then
		local interval = select(1, ...)
		local units = select(2, ...)
		local repeating = select(3, ...)

		self._interval = interval or self._interval
		self._units = units or self._units
		self._repeating = repeating or self._repeating
	end

	if (tonumber(self._interval) > 0) then
		if (LOG ~= nil and type(LOG) == "table") then
			LogTrace("Starting Timer: " .. self._name)
		end

		self._id = C4:AddTimer(self._interval, self._units, self._repeating)
	end
end

function c4_timer:KillTimer()
	if (self._id) then
		self._id = C4:KillTimer(self._id)
	end
end

function c4_timer:TimerStarted()
	return (self._id ~= 0)
end

function c4_timer:TimerStopped()
	return (self._id == 0)
end

function c4_timer:GetTimerInterval()
	return (self._interval)
end

function TimerLibGetNextTimerID()
	gTimerLibTimerCurID = gTimerLibTimerCurID + 1
	return gTimerLibTimerCurID
end

function ON_DRIVER_EARLY_INIT.c4_timer()
	gTimerLibTimers = {}
	gTimerLibTimerCurID = 0
end

function ON_DRIVER_DESTROYED.c4_timer()
	-- Kill open timers
	for k,v in pairs(gTimerLibTimers) do
		v:KillTimer()
	end
end

--[[=============================================================================
    OnTimerExpired(idTimer)

    Description:
    Function called by Director when the specified Control4 timer expires.

    Parameters:
    idTimer(string) - Timer ID of expired timer.
===============================================================================]]
function OnTimerExpired(idTimer)
	for k,v in pairs(gTimerLibTimers) do
		if (idTimer == v._id) then
			if (v._Callback) then
				v._Callback(v._CallbackParam)
			end
		end
	end
end

--[[=============================================================================
    CreateTimer(name, interval, units, callback, repeating, callbackParam)

    Description: 
    Creates a named timer with the given attributes

    Parameters:
    name(string)       - The name of the timer being created
    interval(int)      - The amount of the given time between calls to the
                         timers callback function
    units(string)      - The time of time interval used (e.g. MILLSECONDS, SECONDS, MINUTES, HOURS)
    callback(string)   - The function to call when the timer expires
    repeating(bool)    - Parameter indicating whether the timer should be
                         called repeatedly until cancelled
    callbackParam(...) - Parameters to be passed to the callback function

    Returns:
    A handle to the timer
===============================================================================]]
function CreateTimer(name, interval, units, callback, repeating, callbackParam)
	timer = c4_timer:new(name, interval, units, callback, repeating, callbackParam)
	return timer
end

--[[=============================================================================
    StartTimer(handle, ...)

    Description: 
    Starts the timer created by calling the CreateTimer functions

    Parameters:
    handle(timer)   - Handle to a created timer object
    interval(int)   - The amount of the given time between calls to the
                      timers callback function
    units(string)   - The time of time interval used (e.g. SECONDS, MINUTES, ...)
    repeating(bool) - Parameter indicating whether the timer should be
                      called repeatedly until cancelled

    Returns:
    None
===============================================================================]]
function StartTimer(handle, ...)
	handle:StartTimer(...)
end

--[[=============================================================================
    KillTimer(handle)

    Description: 
    Starts the timer created by calling the CreateTimer functions

    Parameters:
    handle(timer) - Handle to a created timer object

    Returns:
    None
===============================================================================]]
function KillTimer(handle)
	handle:KillTimer()
end

--[[=============================================================================
    TimerStarted(handle)

    Description: 
    Identifies whether a timer has been started or not

    Parameters:
    handle(timer) - Handle to a created timer object

    Returns:
    Returns true if a the given timer handle has been started, or false otherwise
===============================================================================]]
function TimerStarted(handle)
	return handle:TimerStarted()
end

--[[=============================================================================
    TimerStopped(handle)

    Description: 
    Identifies whether a timer has been stopped or not

    Parameters:
    handle(timer) - Handle to a created timer object

    Returns:
    Returns true if a the given timer handle has been stopped, or false otherwise
===============================================================================]]
function TimerStopped(handle)
	return handle:TimerStopped()
end

--[[=============================================================================
    GetTimerInterval(handle)

    Description: 
    Gets the interval setting of the given timer

    Parameters:
    handle(timer) - Handle to a created timer object

    Returns:
    Returns the interval setting of the given timer
===============================================================================]]
function GetTimerInterval(handle)
	return handle:GetTimerInterval()
end

--[[=============================================================================
    c4_timer Unit Tests
===============================================================================]]
function __test_c4_timer()
	require "test.C4Virtual"
	require "lib.c4_log"
	require "common.c4_init"

	OnDriverInit()

	local LOG = c4_log:new("test_c4_timer")
	LOG:SetLogLevel(5)
	LOG:OutputPrint(true)

	function OnTestTimerExpired()
		c4Timer:KillTimer()
	end

	-- create an instance of the timer
	c4Timer = c4_timer:new("Test", 45, "MINUTES", OnTestTimerExpired)

	assert(c4Timer._id == 0, "_id is not equal to '0' it is: " .. c4Timer._id)
	c4Timer:StartTimer()
	assert(c4Timer._id == 10001, "_id is not equal to '10001' it is: " .. c4Timer._id)
	assert(c4Timer:TimerStarted() == true, "TimerStarted is not equal to true it is: " .. tostring(c4Timer:TimerStarted()))
	assert(c4Timer:TimerStopped() == false, "TimerStopped is not equal to false it is: " .. tostring(c4Timer:TimerStopped()))
	OnTimerExpired(c4Timer._id)
	assert(c4Timer:TimerStarted() == false, "TimerStarted is not equal to false it is: " .. tostring(c4Timer:TimerStarted()))
	assert(c4Timer:TimerStopped() == true, "TimerStopped is not equal to true it is: " .. tostring(c4Timer:TimerStopped()))
end end)
package.preload['lib.c4_xml'] = (function (...)
--[[=============================================================================
    Functions for parsing and managing xml

    Copyright 2016 Control4 Corporation. All Rights Reserved.
===============================================================================]]

if (TEMPLATE_VERSION ~= nil) then
	TEMPLATE_VERSION.c4_xml = "2016.01.08"
end

--[[=============================================================================
    GetParsedXmlNode(tXml, node)

    Description: 
    Find the specified node within the given table

    Parameters:
    tXml(table)  - Xml fragment containing the node we are looking for
    node(string) - The name of the node

    Returns:
    nil or the specified node within the table
===============================================================================]]
function GetParsedXmlNode(tXml, node)
	for k, v in pairs(tXml["ChildNodes"]) do
		if (v["Name"] == node) then
			return v["ChildNodes"]
		end
	end

	return nil
end

--[[=============================================================================
    GetParsedXmlValuesByKey(tXml, node, key, keyIsNumber)

    Description: 
    Find the specified node element within the given table

    Parameters:
    tXml(table)       - Xml fragment to find the value in
    node(string)      - The name of the node
    key(string)       - The name of the key
    keyIsNumber(bool) - Indicates whether the table index is a number or a string

    Returns:
    nil or a table of the found values within the Xml
===============================================================================]]
function GetParsedXmlValuesByKey(tXml, node, key, keyIsNumber)
	local tParams = {}

	keyIsNumber = keyIsNumber or false
	for k,v in pairs(tXml) do
		if (v["Name"] == node) then
			local keyValue
			
			-- get the key
			for nodeKey, nodeValue in pairs(v["ChildNodes"]) do
				if (nodeValue["Name"] == key) then
					if (keyIsNumber == true) then
						keyValue = tonumber(nodeValue.Value)
					else
						keyValue = tostring(nodeValue.Value)
					end
					break
				end
			end

			-- get other tags
			tParams[keyValue] = {}
			for nodeKey, nodeValue in pairs(v["ChildNodes"]) do
				if (nodeValue["Name"] ~= key) then
					tParams[keyValue][nodeValue.Name] = nodeValue.Value
				end
			end
		end
	end

	return tParams
end

--[[=============================================================================
    GetParsedXmlVaulesByKeyAttribute(tXml, node, key, keyIsNumber)

    Description: 
    Find the specified node attribute within the given table

    Parameters:
    tXml(table)       - Xml fragment to find the value in
    node(string)      - The name of the node
    key(string)       - The name of the key
    keyIsNumber(bool) - Indicates whether the table index is a number or a string

    Returns:
    nil or a table of the found values within the Xml
===============================================================================]]
function GetParsedXmlVaulesByKeyAttribute(tXml, node, key, keyIsNumber)
	local tParams = {}

	keyIsNumber = keyIsNumber or false
	for k,v in pairs(tXml["ChildNodes"]) do
		if (v["Name"] == node) then
			local keyValue

			if (keyIsNumber == true) then
				keyValue = tonumber(v["Attributes"][key])
			else
				keyValue = v["Attributes"][key]
			end
			
			tParams[keyValue] = v["Value"]
		end
	end

	return tParams
end

--[[=============================================================================
    BuildSimpleXml(tag, tData, escapeValue)

    Description: 
    Find the specified node within the given table

    Parameters:
    tag(string)       - Xml tag name to create
    tData(table)      - key value pairs that will be added as elements under tag
    escapeValue(bool) - Indicates whether the values should be escaped or not

    Returns:
    nil or an Xml fragment the specified node within the table
===============================================================================]]
function BuildSimpleXml(tag, tData, escapeValue)
	local xml = ""
	
	if (tag ~= nil) then
		xml = "<" .. tag .. ">"
	end
	
	for k,v in pairs(tData) do
		xml = xml .. "<" .. k
		if (type(v) == "table") then
			-- handle attributes
			for kAttrib, vAttrib in pairs(v.attributes) do
				xml = xml .. ' ' .. kAttrib .. '=\"' .. vAttrib .. '\"'
			end
			xml = xml .. ">" .. InsertValue(v.value, escapeValue) .. "</" .. k .. ">"
		else
			xml = xml .. ">" .. InsertValue(v, escapeValue) .. "</" .. k .. ">"
		end
	end
	
	if (tag ~= nil) then
		xml = xml .. "</" .. tag .. ">"
	end

	--DbgTrace("BuildSimpleXml(): " .. xml)

	return xml
end

--[[=============================================================================
    InsertValue(value, escapeValue)

    Description: 
    Return the given value if escapeValue is true it will escape any special
    characters in the value

    Parameters:
    value(string)     - value to be manipulated
    escapeValue(bool) - Indicates whether the values should be escaped or not

    Returns:
    The value given or an escaped value if specified
===============================================================================]]
function InsertValue(value, escapeValue)

	if (escapeValue) then
		value = C4:XmlEscapeString(tostring(value))
	end

	return value
end

--[[=============================================================================
    StartElement(tag)

    Description: 
    Wrap the given tag as an Xml element (i.e. <tag>)

    Parameters:
    tag(string) - The name of the item to be wrapped as a starting Xml element

    Returns:
    The value wrapped as Xml tag
===============================================================================]]
function StartElement(tag)
	return "<" .. tag .. ">"
end

--[[=============================================================================
    EndElement(tag)

    Description: 
    Wrap the given tag as an Xml end element (i.e. </tag>)

    Parameters:
    tag(string) - The name of the item to be wrapped as a ending Xml element

    Returns:
    The value wrapped as ending Xml tag
===============================================================================]]
function EndElement(tag)
	return "</" .. tag .. ">"
end

--[[=============================================================================
    AddElement(tag, data)

    Description: 
    Wrap the given tag and value as an Xml element (i.e. <tag>data</tag>)

    Parameters:
    tag(string)  - The name of the item to be wrapped as an Xml element
    data(string) - The value of the Xml element being created

    Returns:
    The value wrapped as Xml tag and value
===============================================================================]]
function AddElement(tag, data)
	LogTrace("tag = " .. tag)
	LogTrace("data = " .. data)
	
	return "<" .. tag .. ">" .. data .. "</" .. tag .. ">"
end
 end)
package.preload['actions'] = (function (...)
--[[=============================================================================
    Lua Action Code

    Copyright 2016 Control4 Corporation. All Rights Reserved.
===============================================================================]]

-- This macro is utilized to identify the version string of the driver template version used.
if (TEMPLATE_VERSION ~= nil) then
	TEMPLATE_VERSION.actions = "2016.01.08"
end

-- TODO: Create a function for each action defined in the driver

function LUA_ACTION.TemplateVersion()
	TemplateVersion()
end


function LUA_ACTION.PrintVolumeCurve()
    print("===== Volume Curve =====")
    for j,k in pairs(tVolumeCurve) do
	   print(j,k)
    end
end

function LUA_ACTION.ACTION_GetSystemStatus()
	EX_CMD.GetSystemStatus()
end

function LUA_ACTION.ACTION_SetDeviceReboot()
	EX_CMD.SetDeviceReboot()
end


function LUA_ACTION.ACTION_SetPowerMode(tParams)
	EX_CMD.SetPowerMode(tParams)
end

function LUA_ACTION.ACTION_SetBeepMode(tParams)
	EX_CMD.SetBeepMode(tParams)
end

function LUA_ACTION.ACTION_SetPannelMode(tParams)
	EX_CMD.SetPannelMode(tParams)
end

 end)
package.preload['av_path'] = (function (...)
--[[=============================================================================
    AVSwitch Advance AV Path Handling Functions

    Copyright 2015 Control4 Corporation. All Rights Reserved.
===============================================================================]]

function ON_DRIVER_LATEINIT.avpath()
     --[[
	   TODO: 	 If advanced path handling is required, uncomment the C4:SendToProxy call below which will notify the proxy 
			 that your protocol driver will handle the validation of all valid paths. This is accomplished via the
			 IS_AV_OUTPUT_TO_INPUT_VALID() proxy command which reports all paths based upon the driver connections and current 
			 project bindings. The value that you return with this function will flag a given path as valid or invalid. 
	--]]
	
     --C4:SendToProxy(AVSWITCH_PROXY_BINDINGID, 'PROTOCOL_WILL_HANDLE_AV_VALID', {})
end


--[[
IS_AV_OUTPUT_TO_INPUT_VALID PROXY COMMAND
PARAMS:
	[PARAM NAME]				(Sample Data)		[DESCRIPTION]
	
	Params_idRoom 				(31)				Room Id - INTEGER
	Params_bindingType 			(6)				Connection Type - INTEGER (Video=5, Audio=6, Room Binding=7)
	
	Consumer_idBinding 			(1000)			Input Connection Id 	- INTEGER
	Consumer_avClass 			(10)				Input Connection Class 	- INTEGER
	Consumer_sClass 			(HDMI)			Input Connection Class 	- STRING
	
	Provider_idBinding			(2009)			Output Connection Id 	- INTEGER
	Provider_sClass			(HDMI)			Output Connection Class 	- STRING
	Provider_avClass			(10)				Output Connection Class 	- INTEGER
		
	Params_pathType 			(0)				UNKNOWN (Always returns zero)
	Consumer_sConnName 			()				UNKNOWN (Always returns NIL)
	Provider_sConnName 			()				UNKNOWN (Always returns NIL)
	Params_idSource 			(0)				UNKNOWN (Always returns zero)
	Params_bIsSource 			(0)				UNKNOWN (Always returns zero)
	Params_idCurrentSource 		(0)				UNKNOWN (Always returns zero)
	Params_idQueue 			(0)				UNKNOWN (Always returns zero)
	Params_idMedia				(0)				UNKNOWN (Always returns zero)
	Params_sMediaType			()				UNKNOWN (Always returns NIL)
	
RETURN VALUES:
     "True"									The reported path is valid
     "False"									The reported path is invalid

This command is sent from the proxy for each valid connection path. A path is created for each input class to each output class for each approriate room binding type.
We need clarification of the frequency on which this commands sends the same path.
Examples:
	* One HDMI INPUT to One HDMI OUTPUT bound to a Room with 3 bound endpoints (Audio, Video & Video's Audio) will receiver 6 commands - 4 audio (type 6) and 2 video (type 5)
	* One DIGITAL_COAX INPUT to one HDMI OUTPUT & one STEREO OUTPUT bound to a Room with 3 bound endpoints (Audio, Video & Video's Audio) will receiver 4 commands - 4 audio (type 6) and 0 video (type 5)
	* One DIGITAL_COAX INPUT to one STEREO OUTPUT bound to a Room with 3 bound endpoints (Audio, Video & Video's Audio) will receiver 2 commands - 2 audio (type 6) and 0 video (type 5)
--]]
function IS_AV_OUTPUT_TO_INPUT_VALID(params)
    --[[
	   TODO: If all paths are not valid due to signal conversion limitations on your device, uncomment the call to 
			 the isPathValid() function below. You will also need to create the validation logic based upon the 
			 devices conversion capabilities. Note that if all paths are valid then just leave the default values in place.
    --]]
    
    --local pathIsValid, pathStatus = isPathValid(params)
    
    --TODO: Comment these lines if you uncomment the line above...
    local pathIsValid =  "True"
    local pathStatus = "VALID"
    
    --[[
	   A key benefit of the IS_AV_OUTPUT_TO_INPUT_VALID() function is to build mapping tables that enable your 
	   driver to make decsions based upon actual project bindings and room associations.
	   This can be beneifical in implementing EDID managment on HDMI matrices, mirroring outputs for delivery 
	   of audio and video to separate devices (i.d. TV & Receiver), and selection of separate audio sources 
	   while keeping same video source
    --]]
    updateMappingTables(params,pathStatus)
    
    return pathIsValid
end

function isPathValid(params)
    local consumer_idBinding 	= tonumber(params["Consumer_idBinding"])	-- we are consuming the source, so the consumer binding is the source
    local provider_idBinding 	= tonumber(params["Provider_idBinding"]) 	-- we are providing the output, to the output is the provider binding  
    local consumer_class    	= params["Consumer_sClass"]
    local provider_class    	= params["Provider_sClass"]
    
    --here is sample logic for illustration only. you will need to contruct the logic to match the signal conversion capabilities of your device
    if ((consumer_class == "DIGITAL_COAX") and (provider_class == "HDMI") and (Properties["SPDIF to HDMI Connections"] == "DISABLED")) then
		return "False","INVALID"
    elseif ((consumer_class == "HDMI") and (provider_class == "STEREO") and (Properties["Analog Audio Matrix to Matrix Mode"] == "ENABLED")) then
          --lock each HDMI input to only one STEREO output, detemined by id (input1 to output1, etc.)
		if (consumer_idBinding % 1000 == provider_idBinding % 1000) then
			return "True","VALID"
		else	
			return "False","INVALID"
		end
    else
		return "True","VALID"
    end
end 

--[[
	Proxy Command: BINDING_CHANGE_ACTION
	Parameters:
		idBinding: proxybindingid of proxy bound to input connection
		output: mod 1000 value of Output Connection id	
		input: mod 1000 value of Input Connection id
--]]
function BINDING_CHANGE_ACTION(params)
  --reintitalizing mapping tables to handle deleted bindings
  --current bindings will be re-added during input selection and any other instances where IS_AV_OUTPUT_TO_INPUT_VALID is called
  gVideoProviderToRoomMap = {}
  gAudioProviderToRoomMap = {}
  gLastReportedAVPaths = {}
  
  return nil
end

function updateMappingTables(params, pathStatus)
    --table to track path information
    local t = {
	   ["RoomID"]  				= tonumber(params["Params_idRoom"]),
	   ["PathType"]  				= tonumber(params["Params_bindingType"]),
	   ["PathStatus"]  				= pathStatus,
	   ["InputConnectionID"]  		= tonumber(params["Consumer_idBinding"]),
	   ["InputConnectionClassID"]  	= tonumber(params["Consumer_avClass"]),
	   ["InputConnectionClass"]  		= params["Consumer_sClass"],
	   ["OutputConnectionID"]  		= tonumber(params["Provider_idBinding"]),
	   ["OutputConnectionClassID"]  	= tonumber(params["Provider_avClass"]),
	   ["OutputConnectionClass"]  	= params["Provider_sClass"],
    }
	
    --build a unique key to avoid duplicate entries...
    local key = params["Params_idRoom"] .. ":" .. params["Params_bindingType"] .. ":" .. params["Provider_idBinding"] ..  ":" .. params["Provider_avClass"] .. ":" .. params["Consumer_idBinding"] ..  ":" .. params["Consumer_avClass"]
    gLastReportedAVPaths[key] = t   
    
	if (gAVPathType[tonumber(params["Params_bindingType"])] == "VIDEO") then
		--Video Output to Room mapping table
		gVideoProviderToRoomMap[params["Provider_idBinding"]] = params["Params_idRoom"]
	elseif (gAVPathType[tonumber(params["Params_bindingType"])] == "AUDIO") then
		--Audio Output Room mapping table 
		local apKey = params["Params_idRoom"] .. ":" .. params["Provider_idBinding"]
		gAudioProviderToRoomMap[apKey] = {["RoomID"] = params["Params_idRoom"], ["OutputConnectionID"] = params["Provider_idBinding"]}
	end	
end

function getMirroredOutputID(output_id)
	LogTrace("getMirroredOutputID, OUTPUT_ID=" .. output_id)
	local output, room_id
	
	--find audio leg of mirrored pair
	room_id = gVideoProviderToRoomMap[output_id]
	if (room_id ~= nil) then
		for j,k in pairs(gAudioProviderToRoomMap) do 
			if ( (tonumber(k.OutputConnectionID) >= 2000) and (tonumber(k.OutputConnectionID) <= 2999)) then --mirrored zone must be an HDMI output, not an audio output
				if (k.OutputConnectionID ~= output_id) and (k.RoomID == room_id) then
					--output = (k.OutputConnectionID % 1000) 
					return k.OutputConnectionID
				end
			end
		end
	end
	
	--find video leg of mirrored pair
	local room, out
	for j,k in pairs(gAudioProviderToRoomMap) do 
	    room, out = string.match(j, "(.+):(.+)")
		if (out == output_id) then
			room_id = room
			for o,r in pairs(gVideoProviderToRoomMap) do 
			  if (r == room_id) then
				if ( (tonumber(o) >= 2000) and (tonumber(o) <= 2999)) then --mirrored zone must be an HDMI output, not an audio output
					if (o ~= output_id) and (r == room_id) then
						--output = (o % 1000) 
						return o
					end
				end			  
			  end
			end
		end	
	end	

	return -1
  
end

function getPathTypeFromOutputID(output_id)
  --mirrored zone ids are all in video range
  for j,k in pairs(gLastReportedAVPaths) do
    if (output_id == tonumber(k.OutputConnectionID)) then
      local pathType = gAVPathType[k.PathType]
	 return pathType
    end
  end  
end

function getMirroredOutputState(output_id)
  LogTrace("getMirroredOutputState(Output = " .. tOutputConnMapId2Name[output_id] .. ")")
  local mirrored_output_id = getMirroredOutputID(output_id)  
  if (mirrored_output_id == -1) then
    --no mirror zone
	return "NO MIRROR ZONE"  
  else
    if (getPathTypeFromOutputID(output_id) == "AUDIO") then
	   --this is the Audio Zone, so the Mirrored Zone is Video
	   return "AUDIO ZONE WITH MIRRORED VIDEO ZONE"
    else 
	   return "VIDEO ZONE WITH MIRRORED AUDIO ZONE"
    end	 
  end
end

function startAudioSelectionTimer(output)
  if (output == 0) then
    gAudioSelectionInProgressOutput0Timer:StartTimer() 
  elseif (output == 1) then
    gAudioSelectionInProgressOutput1Timer:StartTimer() 
  elseif (output == 2) then
    gAudioSelectionInProgressOutput2Timer:StartTimer() 
  elseif (output == 3) then
    gAudioSelectionInProgressOutput3Timer:StartTimer()  
  else
	LogTrace("startAudioSelectionTimer, invalid output = " .. output)
  end
end

function startHDMIAudioSelectionTimer(output)
  if (output == 0) then
    gHDMIAudioSelectionInProgressOutput0Timer:StartTimer() 
  elseif (output == 1) then
    gHDMIAudioSelectionInProgressOutput1Timer:StartTimer() 
  elseif (output == 2) then
    gHDMIAudioSelectionInProgressOutput2Timer:StartTimer() 
  elseif (output == 3) then
    gHDMIAudioSelectionInProgressOutput3Timer:StartTimer()     	
  else
	LogTrace("startHDMIAudioSelectionTimer, invalid output = " .. output)
  end
end

function isAudioSelectionInProgress(output_id)
  local bInProgress = false
  local output
  local room_id = gVideoProviderToRoomMap[output_id]
  for j,k in pairs(gAudioProviderToRoomMap) do 
	if ( (tonumber(k.OutputConnectionID) >= 4000) and (tonumber(k.OutputConnectionID) <= 4999)) then --zone must be an audio output, not an HDMI output
		if (k.RoomID == room_id) then
		  output = (k.OutputConnectionID % 1000)
		  bInProgress = isAudioSelectionInProgressByOutput(output)
		  if (bInProgress) then break end
		end
	end	
  end
  
  if (output == nil) then 
    if (room_id == nil) then --commands coming from programming may not have roomid
      LogTrace("isAudioSelectionInProgress, Selection in progress is False for Video Output("  .. output_id .. "), no Audio Output is mapped.")
    else 
	 LogTrace("isAudioSelectionInProgress, Selection in progress is False for Video Output("  .. output_id .. ") in room(" .. room_id .. "), no Audio Output is mapped.")
    end
    
    return false 
  end
  
  local sInProgress
  if (bInProgress == true) then
    sInProgress = "True"
  else
    sInProgress = "False"
  end
  
  --since we only know of the valid paths, not the actual path that director has taken in a matrix to matrix setup, this test is not conclusive...
  --we will abort the disconnect if any valid path has a audio selection in progress...
  LogTrace("isAudioSelectionInProgress, Audio Selection in progress is " .. sInProgress .. " for Video Output("  .. output_id .. ") in room(" .. room_id .. ") is mapped to Audio Output(" .. output .. ").")
  
  return bInProgress 
  
end

function isAudioSelectionInProgressByOutput(output)
  local bInProgress = false
  if (output == 0) then
    if(gAudioSelectionInProgressOutput0Timer:TimerStarted()) then
      bInProgress = true
    end
  elseif (output == 1) then
    if(gAudioSelectionInProgressOutput1Timer:TimerStarted()) then
      bInProgress = true
    end	
  elseif (output == 2) then
    if(gAudioSelectionInProgressOutput2Timer:TimerStarted()) then
      bInProgress = true
    end 
  elseif (output == 3) then
    if(gAudioSelectionInProgressOutput3Timer:TimerStarted()) then
      bInProgress = true
    end
  else
	LogTrace("isAudioSelectionInProgressByOutput, bogus output = " .. output)
  end
  
  return bInProgress
  
end

function isHDMIAudioSelectionInProgress(output, output_id)
  local bInProgress = false

  if (output == 0) then
    if(gHDMIAudioSelectionInProgressOutput0Timer:TimerStarted()) then
      bInProgress = true
    end  
  elseif (output == 1) then
    if(gHDMIAudioSelectionInProgressOutput1Timer:TimerStarted()) then
      bInProgress = true
    end
  elseif (output == 2) then
    if(gHDMIAudioSelectionInProgressOutput2Timer:TimerStarted()) then
      bInProgress = true
    end 
  elseif (output == 3) then
    if(gHDMIAudioSelectionInProgressOutput3Timer:TimerStarted()) then
      bInProgress = true
    end
  else
	LogTrace("isHDMIAudioSelectionInProgress, bogus output = " .. output)
  end
  
  --check if mirrored zone has an input selection in progress
  if (bInProgress == false) then
	local mirrored_output_id = getMirroredOutputID(output_id)
	bInProgress = isHDMIAudioSelectionInProgressInMirroredZone(mirrored_output_id)
	return bInProgress
  end	
  
  local sInProgress
  if (bInProgress == true) then
    sInProgress = "True"
  else
    sInProgress = "False"
  end
  
  LogTrace("isHDMIAudioSelectionInProgress, Selection in progress is " .. sInProgress .. " for Output(" .. output .. ").")
  return bInProgress 
  
end

function isHDMIAudioSelectionInProgressInMirroredZone(mirrored_output_id)
  local output = mirrored_output_id % 1000
  local bInProgress = false

  if (output == 0) then
    if(gHDMIAudioSelectionInProgressOutput0Timer:TimerStarted()) then
      bInProgress = true
    end  
  elseif (output == 1) then
    if(gHDMIAudioSelectionInProgressOutput1Timer:TimerStarted()) then
      bInProgress = true
    end
  elseif (output == 2) then
    if(gHDMIAudioSelectionInProgressOutput2Timer:TimerStarted()) then
      bInProgress = true
    end 
  elseif (output == 3) then
    if(gHDMIAudioSelectionInProgressOutput3Timer:TimerStarted()) then
      bInProgress = true
    end
  else
	LogTrace("isHDMIAudioSelectionInProgressInMirroredZone, bogus output = " .. output)
  end
  
  local sInProgress
  if (bInProgress == true) then
    sInProgress = "True"
  else
    sInProgress = "False"
  end
  
  LogTrace("isHDMIAudioSelectionInProgressInMirroredZone, Selection in progress is " .. sInProgress .. " for Output(" .. output .. ").")
  return bInProgress 
  
end


--[[=============================================================================
    Timer Expriation Code
===============================================================================]]
function OnAudioSelectionInProgressOutput0TimerExpired()
    LogTrace("OnAudioSelectionInProgressOutput0TimerExpired()")
    gAudioSelectionInProgressOutput0Timer:KillTimer()
end

function OnAudioSelectionInProgressOutput1TimerExpired()
    LogTrace("OnAudioSelectionInProgressOutput1TimerExpired()")
    gAudioSelectionInProgressOutput1Timer:KillTimer()
end

function OnAudioSelectionInProgressOutput2TimerExpired()
    LogTrace("OnAudioSelectionInProgressOutput2TimerExpired()")
    gAudioSelectionInProgressOutput2Timer:KillTimer()
end

function OnAudioSelectionInProgressOutput3TimerExpired()
    LogTrace("OnAudioSelectionInProgressOutput3TimerExpired()")
    gAudioSelectionInProgressOutput3Timer:KillTimer()
end


function OnHDMIAudioSelectionInProgressOutput0TimerExpired()
    LogTrace("OnHDMIAudioSelectionInProgressOutput0TimerExpired()")
    gHDMIAudioSelectionInProgressOutput0Timer:KillTimer()
end

function OnHDMIAudioSelectionInProgressOutput1TimerExpired()
    LogTrace("OnHDMIAudioSelectionInProgressOutput1TimerExpired()")
    gHDMIAudioSelectionInProgressOutput1Timer:KillTimer()
end

function OnHDMIAudioSelectionInProgressOutput2TimerExpired()
    LogTrace("OnHDMIAudioSelectionInProgressOutput2TimerExpired()")
    gHDMIAudioSelectionInProgressOutput2Timer:KillTimer()
end

function OnHDMIAudioSelectionInProgressOutput3TimerExpired()
    LogTrace("OnHDMIAudioSelectionInProgressOutput3TimerExpired()")
    gHDMIAudioSelectionInProgressOutput3Timer:KillTimer()
end
 end)
package.preload['avswitch_init'] = (function (...)
--[[=============================================================================
    AVSwitch Protocol Initialization Functions

    Copyright 2015 Control4 Corporation. All Rights Reserved.
===============================================================================]]

-- This macro is utilized to identify the version string of the driver template version used.
if (TEMPLATE_VERSION ~= nil) then
	TEMPLATE_VERSION.device_messages = "2015.03.31"
end


PROTOCOL_DECLARATIONS = {}

function ON_DRIVER_EARLY_INIT.avswitch_init()

end

function ON_DRIVER_INIT.avswitch_init()
	--LogTrace("ON_DRIVER_INIT.ProtocolDeclarations()")
	for k,v in pairs(PROTOCOL_DECLARATIONS) do
		if (PROTOCOL_DECLARATIONS[k] ~= nil and type(PROTOCOL_DECLARATIONS[k]) == "function") then
			PROTOCOL_DECLARATIONS[k]()
		end
	end
end

function ON_DRIVER_LATEINIT.avswitch_init()
end

function PROTOCOL_DECLARATIONS.CommandsTableInit_Serial()
	LogTrace("PROTOCOL_DECLARATIONS.CommandsTableInit_Serial()")

	CMDS = {
		--index:  Proxy Command Name
		--value:  Protocol Command Data

		--Power
		["ON"]             = "s power on",
		["OFF"]            = "s power off",
	}

	CMDS[AVSWITCH_PROXY_BINDINGID] = {}

end

function PROTOCOL_DECLARATIONS.InputOutputTableInit()
    LogTrace("PROTOCOL_DECLARATIONS.InputOutputTableInit()")
    ----------------------------------------- [*COMMAND/RESPONSE HELPER TABLES*] -----------------------------------------

    tOutputCommandMap = {
	   --index:  value of Output Connection id
	   --value:  Protocol Command Data
	   [0] = "1",
	   [1] = "2",
	   [2] = "3",
	   [3] = "4",
	   [4] = "5",
	   [5] = "6",
	   [6] = "7",
	   [7] = "8",
	   [8] = "9",
	   [9] = "10",
	   [10] = "11",
	   [11] = "12",
	   [12] = "13",
	   [13] = "14",
	   [14] = "15",
	   [15] = "16",
    }


    tInputCommandMap = {
	   [0] = "1",
	   [1] = "2",
	   [2] = "3",
	   [3] = "4",
	   [4] = "5",
	   [5] = "6",
	   [6] = "7",
	   [7] = "8",
	   [8] = "9",
	   [9] = "10",
	   [10] = "11",
	   [11] = "12",
	   [12] = "13",
	   [13] = "14",
	   [14] = "15",
	   [15] = "16",
    }

	tAudioInputMap = {
	   [1000] = "1",
	   [1001] = "2",
	   [1002] = "3",
	   [1003] = "4",
	   [1004] = "5",
	   [1005] = "6",
	   [1006] = "7",
	   [1007] = "8",
	   [3000] = "9",
	   [3001] = "10",
	   [3002] = "11",
	   [3003] = "12",
	   [3004] = "13",
	   [3005] = "14",
	   [3006] = "15",
	   [3007] = "16",
	}
	----------------------------------------- [*I/O HELPER TABLES*] -----------------------------------------
	--[[
    tOutputConnMapId2Name = {
		--index:  value of Output Connection id
		--value:  Output Connection Name
		[2000] = "HDMI_A",
		[2001] = "HDMI_B",
		[2002] = "HDMI_C",
		[2003] = "HDMI_D",
		[2004] = "HDMI_E",
		[2005] = "HDMI_F",
		[2006] = "HDMI_G",
		[2007] = "HDMI_H",
	     [2008] = "HDMI_I",
		[2009] = "HDMI_J",
		[2010] = "HDMI_K",
		[2011] = "HDMI_L",
		[2012] = "HDMI_M",
		[2013] = "HDMI_N",
		[2014] = "HDMI_O",
		[2015] = "HDMI_P",
		[4008] = "AUDIO_A",
		[4009] = "AUDIO_B",
		[4010] = "AUDIO_C",
		[4011] = "AUDIO_D",
		[4012] = "AUDIO_E",
		[4013] = "AUDIO_F",
		[4014] = "AUDIO_G",
		[4015] = "AUDIO_H",
	}
    tOutputConnMapName2Id = ReverseTable(tOutputConnMapId2Name)
	--]]
end

function PROTOCOL_DECLARATIONS.PowerCommandsTableInit_Serial()
	LogTrace("PROTOCOL_DECLARATIONS.PowerCommandsTableInit_Serial()")

	tPowerCommandMap = {
		--index:  mod 1000 value of Output Connection id
		--value:  Protocol Command Data (Power)
		[0] = "",
		[1] = "",
		[2] = "",
		[3] = "",
	}
end

function PROTOCOL_DECLARATIONS.VolumeCommandsTableInit_Serial()
	LogTrace("PROTOCOL_DECLARATIONS.VolumeCommandsTableInit_Serial()")

end
--Reverse the table
function ReverseTable(a)
	local b = {}
	for k,v in pairs(a) do b[v] = k end
	return b
end

 end)
package.preload['connections'] = (function (...)
--[[=============================================================================
    Functions for managing the status of the drivers bindings and connection state

    Copyright 2015 Control4 Corporation. All Rights Reserved.
===============================================================================]]
require "common.c4_network_connection"
require "common.c4_serial_connection"
require "common.c4_ir_connection"
require "common.c4_url_connection"

-- This macro is utilized to identify the version string of the driver template version used.
if (TEMPLATE_VERSION ~= nil) then
	TEMPLATE_VERSION.connections = "2015.03.31"
end

-- constants
COM_USE_ACK = false
COM_COMMAND_DELAY_MILLISECONDS = 250
COM_COMMAND_RESPONSE_TIMEOUT_SECONDS = 4

NETWORK_PORT = 8000
IR_BINDING_ID = 2
SERIAL_BINDING_ID = 1
NETWORK_BINDING_ID = 6001

--[[=============================================================================
    OnSerialConnectionChanged(idBinding, class, bIsBound)

    Description:
    Function called when a serial binding changes state(bound or unbound).

    Parameters:
    idBinding(int) - ID of the binding whose state has changed (SERIAL_BINDING_ID).
    class(string)  - Class of binding that has changed.
                     A single binding can have multiple classes(i.e. COMPONENT,
                     STEREO, RS_232, etc).
                     This indicates which has been bound or unbound.
    bIsBound(bool) - Whether the binding has been bound or unbound.

    Returns:
    None
===============================================================================]]
function OnSerialConnectionChanged(idBinding, class, bIsBound)

end

--[[=============================================================================
    OnIRConnectionChanged(idBinding, class, bIsBound)

    Description:
    Function called when an IR binding changes state(bound or unbound).

    Parameters:
    idBinding(int) - ID of the binding whose state has changed (SERIAL_BINDING_ID).
    class(string)  - Class of binding that has changed.
                     A single binding can have multiple classes(i.e. COMPONENT,
                     STEREO, RS_232, etc).
                     This indicates which has been bound or unbound.
    bIsBound(bool) - Whether the binding has been bound or unbound.

    Returns:
    None
===============================================================================]]
function OnIRConnectionChanged(idBinding, class, bIsBound)

end

--[[=============================================================================
    OnNetworkConnectionChanged(idBinding, bIsBound)

    Description:
    Function called when a network binding changes state(bound or unbound).

    Parameters:
    idBinding(int) - ID of the binding whose state has changed.
    bIsBound(bool) - Whether the binding has been bound or unbound.

    Returns:
    None
===============================================================================]]
function OnNetworkConnectionChanged(idBinding, bIsBound)

end

--[[=============================================================================
    OnNetworkStatusChanged(idBinding, nPort, sStatus)

    Description:
    Called when the network connection status changes. Sets the updated status of the specified binding

    Parameters:
    idBinding(int)  - ID of the binding whose status has changed
    nPort(int)      - The communication port of the specified bindings connection
    sStatus(string) - "ONLINE" if the connection status is to be set to Online,
                      any other value will set the status to Offline

    Returns:
    None
===============================================================================]]
function OnNetworkStatusChanged(idBinding, nPort, sStatus)

end

--[[=============================================================================
    OnURLConnectionChanged(url)

    Description:
    Function called when the c4_url_connection is created.

    Parameters:
    url - url used by the url connection.

    Returns:
    None
===============================================================================]]
function OnURLConnectionChanged(url)

end

--[[=============================================================================
    DoEvents()

    Description:
    Called from OnSendTimeExpired in the DeviceConnectionBase.

    Parameters:
    None

    Returns:
    None
===============================================================================]]
function DoEvents()
	if (gAVSwitchProxy._VolumeIsRamping == true) then
		for j,k in pairs(gAVSwitchProxy._VolumeRamping) do
			if (k.state == true) then gAVSwitchProxy:ContinueVolumeRamping(j) end
		end
	end

	if (gAVSwitchProxy._MenuNavigationInProgress == true) then
	   SEND_COMMAND_FROM_COMMAND_TABLE(gAVSwitchProxy._MenuNavigationProxyID, gAVSwitchProxy._MenuNavigationOutput, gAVSwitchProxy._MenuNavigationMode)
	end
end

--[[=============================================================================
    SendKeepAlivePollingCommand()

    Description:
    Sends a driver specific polling command to the connected system

    Parameters:
    None

    Returns:
    None
===============================================================================]]
function SendKeepAlivePollingCommand()
    LogTrace("SendKeepAlivePollingCommand()")

	--TODO: set keep alive command for the network connected system if required.
    local command = "r output 0 in source"  --"DIMQSTN"
    LogTrace("command = " .. command)
    PackAndQueueCommand("SendKeepAlivePollingCommand", command)
end
 end)
package.preload['device_messages'] = (function (...)
--[[=============================================================================
    Get, Handle and Dispatch message functions

    Copyright 2015 Control4 Corporation. All Rights Reserved.
===============================================================================]]

-- This macro is utilized to identify the version string of the driver template version used.
-- 此宏用于标识所使用的驱动程序模板版本的版本字符串。
if (TEMPLATE_VERSION ~= nil) then
	TEMPLATE_VERSION.device_messages = "2015.03.31"
end

--[[=============================================================================
    GetMessage()

    Description:
    Used to retrieve a message from the communication buffer. Each driver is
    responsible for parsing that communication from the buffer.

    Parameters:
    None

    Returns:
    A single message from the communication buffer
    GetMessage（）
  
    描述：
    用于从通信缓冲区中检索消息。 每个驱动程序负责从缓冲区解析该通信。
  
    参数：
    没有
  
    返回值：
    来自通信缓冲区的单个消息
===============================================================================]]
function GetMessage()
	local message, pos

	--TODO: Implement a string using Lua captures and patterns which
	--		will be used by string.match to parse out a single message
	--      from the receive buffer(gReceiveBuffer).
	--		The example shown here will return all characters from the beginning of
	--		the gReceiveBuffer up until but not including the first carriage return.
     --TODO：使用Lua捕获和模式实现字符串，string.match将使用它们来从接收缓冲区（gReceiveBuffer）中解析出一条消息。
     --此处显示的示例将返回从gReceiveBuffer的开头直到但不包括第一个回车符的所有字符。

	local pattern = "^(.-)\r()"
	if (gReceiveBuffer:len() > 0) then
	   message, pos = string.match(gReceiveBuffer, pattern)   --分割字符串

	   if (message == nil) then
		  --LOG:Info("Do not have a complete message")
		  return ""
	   end
	   gReceiveBuffer = gReceiveBuffer:sub(pos)              --删除已经分割的字符串
	end

	return message

end

--[[=============================================================================
    HandleMessage(message)]

    Description
    This is where we parse the messages returned from the GetMessage()
    function into a command and data. The call to 'DispatchMessage' will use the
    'name' variable as a key to determine which handler routine, function, should
    be called in the DEV_MSG table. The 'value' variable will then be passed as
    a string parameter to that routine.

    Parameters
    message(string) - Message string containing the function and value to be sent to
                      DispatchMessage

    Returns
    Nothing

    HandleMessage（消息）]

    描述:
        在这里，我们将从GetMessage（）函数返回的消息解析为命令和数据。
        调用“ DispatchMessage”将使用“名称”变量作为键，以确定应在DEV_MSG表中调用哪个处理程序例程，函数。 然后，将'value'变量作为字符串参数传递给该例程。

    参量:
        message（string）-包含要发送到DispatchMessage的函数和值的消息字符串

    Return
        没有
===============================================================================]]
function HandleMessage(message)
	if (type(message) == "table") then
	     LogTrace("HDCVT Feedback Info:")
		LogTrace("HandleMessage. Message is ==>")
		LogTrace(message)
		LogTrace("<==")
	else
		LogTrace("HandleMessage. Message is ==>%s<==", message)
	end

	--TODO: Implement a string using Lua captures and patterns which
	--		will be used by string.match to parse the message
	--      into a name / value pair.
	--		The example shown here will return all alpha characters
	--		up to the first non-alpha character and store them in the "name" variable
	--		the remaining characters will be returned and stored in the "value" variable.

     -- TODO：使用Lua捕获和模式实现字符串
     -- 将由string.match用于解析消息
     -- 成一个名称/值对。
     -- 此处显示的示例将返回所有字母字符
     -- 直到第一个非字母字符，并将它们存储在“名称”变量中
     -- 其余字符将被返回并存储在“值”变量中。
	--local pattern =  "(%a+)(.+)()"

	--local name, value, pos = string.match(message, pattern)
	--name = name or message
	--value = value or ""

	local SerialInfo = string.lower(message)  --反馈设置为小写
	local name =""
	local input_id,output_id
	LogTrace("HandleMessage SerialInfo = "..SerialInfo)
	if(string.find(SerialInfo,"->") ~= nil ) then     --判断字符串中是否存在-> output ，证明该指令为切换指令
	   name = "INPUT"
	   input_id = string.match(SerialInfo,"input(%d+)")
	   output_id = string.match(SerialInfo,"output(%d+)")
	   LogTrace("HandleMessage inputput_id = "..input_id)
	   LogTrace("HandleMessage output_id = "..output_id)
	   DispatchMessage(name, (input_id+999),(output_id+1999))
	elseif(string.find(SerialInfo,": connect") ~= nil or string.find(SerialInfo,": sync") ~= nil)then
		local port,propertyName
		if(string.find(SerialInfo,"hdmi in") ~= nil)then
			port = string.match(SerialInfo,"hdmi input (%d+): connect")
			propertyName = "HDMI Input"
		elseif(string.find(SerialInfo,"hdmi output") ~= nil)then
			port = string.match(SerialInfo,"hdmi output (%d+): connect")
			propertyName = "HDMI Output"
		elseif(string.find(SerialInfo,"hdbt output") ~= nil)then
			port = string.match(SerialInfo,"hdbt output (%d+): connect")
			propertyName = "HDBT Output"
		end
		 DispatchMessage("PROPERTY", propertyName,port)
	end
	--LogTrace("HDCVT name:" .. name.."Input_id:"..Input_id.."Output_id:"..Output_id)
end


--[[=============================================================================
    DispatchMessage(MsgKey, MsgData)

    Description
    Parse routine that will call the routines to handle the information returned
    by the connected system.

    Parameters
    MsgKey(string)  - The function to be called from within DispatchMessage
    MsgData(string) - The parameters to be passed to the function found in MsgKey

    Returns
    Nothing
    DispatchMessage（MsgKey，MsgData）

    描述
    解析例程，该例程将调用例程来处理所连接系统返回的信息。

    参量
    MsgKey（string）-在DispatchMessage中调用的函数
    MsgData（string）-要传递给MsgKey中的函数的参数

    Return
    没有
===============================================================================]]
function DispatchMessage(MsgKey, MsgData1,MsgData2)
	if (DEV_MSG[MsgKey] ~= nil and (type(DEV_MSG[MsgKey]) == "function")) then
		LogInfo("DEV_MSG." .. tostring(MsgKey) .. ":  " .. tostring(MsgData1)..tostring(MsgData2))
		local status, err = pcall(DEV_MSG[MsgKey], MsgData1, MsgData2)
		if (not status) then
			LogError("LUA_ERROR: " .. err)
		end
	else
		LogTrace("HandleMessage: Unhanded command = " .. MsgKey)
	end
end
--[[

]]--
function DEV_MSG.PROPERTY(value1,value2)
	if(value1 ~= nil and value2 ~= nil)then
		LogTrace("DEV_MSG.PROPERTY "..value1.." "..tostring(value2).." Connect Status")
		C4:UpdateProperty(value1.." "..tostring(value2).." Connect Status", "Connected")
	end
end
--[[
TODO: Create DEV_MSG functions for all messages to call Notifies.
	  Sample functions are included below for all applicable notifications.
     待办事项：为所有消息创建DEV_MSG函数以调用通知。
     以下是所有适用通知的示例功能。
--]]

function DEV_MSG.INPUT(value1,value2)
	LogTrace("DEV_MSG.INPUT(), value1 = " .. value1.."value2"..value2)
	--local input_id = tInputConnMapByName[tInputResponseMap[value]].ID 	--value of Input Connection ID (输入连接ID的值)
	--LogTrace("input_id " .. input_id)
	-- TODO: derive and set  "output_id" from value or create separate DEV_MSG functions for each Output Connection
	-- TODO：从值派生和设置“ output_id”，或为每个输出连接创建单独的DEV_MSG函数
	--local output_id = 0 	--输出连接ID的值

	--LogInfo("INPUT_OUTPUT_CHANGED, input = " .. tInputResponseMap[value] .. ", output = " .. tOutputConnMap[output_id])
	gAVSwitchProxy:dev_InputOutputChanged(value1, value2)
end

function DEV_MSG.POWER(value)
	LogTrace("DEV_MSG.POWER(), value = " .. value)

	-- TODO: derive and set  "output" from value or create separate DEV_MSG functions for each Output Connection
	--TODO：从值派生和设置“输出”，或为每个输出连接创建单独的DEV_MSG函数
	local output = 0 	--mod 1000 value of Output Connection ID (mod 1000输出连接ID的值)

	-- TODO: 01 & 00 values will need to be edited based upon the device protocol values
	--indicating if the device is on or off
	--TODO：需要根据设备协议值编辑01和00值
     -- 指示设备是打开还是关闭
	if (value == "01") then
		gAVSwitchProxy:dev_PowerOn(output)
	elseif (value== "00") then
		gAVSwitchProxy:dev_PowerOff(output)
	else
		LogWarn("DEV_MSG.POWER(): value not valid - " .. value)
	end
end

function DEV_MSG.VOLUME(value)
	LogTrace("DEV_MSG.VOLUME(), value = " .. value)

	-- TODO: derive and set "output" and "deviceLevel" from "value"
	--			in the lua code example below string.match is assuming
	--			that the device's output and volume level are separated by a colon
	--			you will need to adjust your parsing based upon the device protocol
	local deviceOutput, deviceLevel =  string.match(value, "^(%d+),(%d+)")

	local output =  deviceOutput --mod 1000 value of Output Connection ID
	--[[
	TODO: You may need to adjust deviceOutput.
			Keep in mind that "output" needs to be the mod 1000 value of Output Connection ID
			The example below assumes that the device output ids start at 1
			but your driver start connection id starts at 0
	--]]
	--local output =  deviceOutput -1.


	local c4Level = deviceLevel
	--[[
	TODO: If the device does not handle volume on a scale of 0 - 100 then the value will need to be converted
			since C4 volume level uses a percentage scale: 0 - 100
			The ConvertVolumeToC4() function is included in this template to handle this conversion.
	--]]
	--local minDeviceLevel = MIN_DEVICE_LEVEL
	--local maxDeviceLevel = MAX_DEVICE_LEVEL
	--local c4Level = ConvertVolumeToC4(deviceLevel, minDeviceLevel, maxDeviceLevel)

	gAVSwitchProxy:dev_VolumeLevelChanged(output, c4Level, deviceLevel)
end

function DEV_MSG.MUTE(value)
	LogTrace("DEV_MSG.MUTE(), value = " .. value)

	-- TODO: derive and set  "output" from value or create separate DEV_MSG functions for each Output Connection
	local output    --mod 1000 value of Output Connection ID

	local state   	--Mute state represented as "True" or "False"
	-- TODO: values "01" & "00" will need to be modified based upon the device protocol specification
	if (value == "01") then
		state = "True"
	elseif (value == "00") then
		state = "False"
	else
		LogWarn("DEV_MSG.MUTE(), value not valid, exiting...")
		return
	end
	gAVSwitchProxy:dev_MuteChanged(output, state)
end

function DEV_MSG.BASS(value)
	LogTrace("DEV_MSG.BASS(), value = " .. value)

	-- TODO: derive and set  "output" from value or create separate DEV_MSG functions for each Output Connection
	local output  --mod 1000 value of Output Connection ID

	-- TODO: set "level", Bass level is represented as a percentage value
	local level

	gAVSwitchProxy:dev_BassLevelChanged(output, level)
end

function DEV_MSG.TREBLE(value)
	LogTrace("DEV_MSG.TREBLE(), value = " .. value)

	-- TODO: derive and set  "output" from value or create separate DEV_MSG functions for each Output Connection
	local output  --mod 1000 value of Output Connection ID

	-- TODO: set "level", Treble level is represented as a percentage value
	local level

	gAVSwitchProxy:dev_TrebleLevelChanged(output, level)
end

function DEV_MSG.BALANCE(value)
	LogTrace("DEV_MSG.BALANCE(), value = " .. value)

	-- TODO: derive and set  "output" from value or create separate DEV_MSG functions for each Output Connection
	local output  --mod 1000 value of Output Connection ID

	-- TODO: set "level", Bass level is represented as a percentage value
	local level

	gAVSwitchProxy:dev_BalanceLevelChanged(output, level)
end

function DEV_MSG.LOUDNESS(value)
	LogTrace("DEV_MSG.LOUDNESS(), value = " .. value)

	-- TODO: derive and set  "output" from value or create separate DEV_MSG functions for each Output Connection
	local output  --mod 1000 value of Output Connection ID

	-- TODO: set "state", Loudness state is represented as "True" or "False" (literal string, not boolean)
	local state
	gAVSwitchProxy:dev_LoudnessChanged(output, state)
end


function hex_dump(buf)
  for byte=1, #buf, 16 do
	local chunk = buf:sub(byte, byte+15)
	io.write(string.format('%08X  ',byte-1))
	chunk:gsub('.', function (c) io.write(string.format('%02X ',string.byte(c))) end)
	io.write(string.rep(' ',3*(16-#chunk)))
	io.write(' ',chunk:gsub('%c','.'),"\n")
  end
end
 end)
package.preload['device_specific_commands'] = (function (...)
--[[=============================================================================
    Copyright 2015 Control4 Corporation. All Rights Reserved.
===============================================================================]]

-- This macro is utilized to identify the version string of the driver template version used.
if (TEMPLATE_VERSION ~= nil) then
	TEMPLATE_VERSION.device_specific_commands = "2015.03.31"
end

--[[=============================================================================
    ExecuteCommand Code

    Define any functions for device specific commands (EX_CMD.<command>)
    received from ExecuteCommand that need to be handled by the driver.
===============================================================================]]
--function EX_CMD.NEW_COMMAND(tParams)
--	LogTrace("EX_CMD.NEW_COMMAND")
--	LogTrace(tParams)
--end

function EX_CMD.GetSystemStatus()
	PackAndQueueCommand("GetSystemStatus","r status")
end
--[[
 * @Author      Ws.Lf
 * @brief		Set the connected device root
 * @param		None
 * @return		None
 * @Remark		None
--]]
function EX_CMD.SetDeviceReboot()
	local command = "s reboot"
	--LOG:Trace("command = " .. command )
	PackAndQueueCommand("SetDeviceReboot",command)
end
--[[
 * @Author     	 	Ws.Lf
 * @brief			Set the connected device power mode
 * @param[tParams]	tParams["mode"] On Off
 * @return			None
 * @Remark			None
--]]
function EX_CMD.SetPowerMode(tParams)
   local command = ""
   LOG:Trace("tParams[mode] = "..tParams["mode"])
   if(tParams["mode"] ~= nil and tParams["mode"] == "On")then
	command = "power 1"
   elseif(tParams["mode"] ~= nil and tParams["mode"] == "Off")then
	command = "power 0"
   end
   --LOG:Trace("command = " .. command)
   PackAndQueueCommand("SetPowerMode",command)
end
--[[
 * @Author      	Ws.Lf
 * @brief			Set the connected device beep mode
 * @param[tParams]	tParams["mode"]On Off
 * @return			None
 * @Remark			None
--]]
function EX_CMD.SetBeepMode(tParams)
   local command = ""
   LOG:Trace("tParams[mode] = "..tParams["mode"])
 -- LOG:Trace("tParams = " .. tParams[mode])
   if(tParams["mode"] ~= nil and tParams["mode"] == "On")then
	command = "s beep 1"
   elseif(tParams["mode"] ~= nil and tParams["mode"] == "Off")then
	command = "s beep 0"
   end
   --LOG:Trace("command = " .. command)
   PackAndQueueCommand("SetBeepMode",command)
end
--[[
 * @Author      	Ws.Lf
 * @brief			Set the connected device pannel mode
 * @param[tParams]	tParams["mode"]Lock Unlock
 * @return			None
 * @Remark			None
--]]
function EX_CMD.SetPannelMode(tParams)
   local command = ""
   LOG:Trace("tParams[mode] = "..tParams["mode"])
 -- LOG:Trace("tParams = " .. tParams[mode])
   if(tParams["mode"] ~= nil and tParams["mode"] == "Lock")then
	command = "s lock 1"
   elseif(tParams["mode"] ~= nil and tParams["mode"] == "Unlock")then
	command = "s lock 0"
   end
   --LOG:Trace("command = " .. command)
   PackAndQueueCommand("SetPannelMode",command)
end


function EX_CMD.SetLcdOnTime(tParams)
    local command = ""
	if(tParams["mode"]=="off")then
		command = "s lcd on time 0"
	elseif(tParams["mode"]=="always")then
		command = "s lcd on time 1"
	elseif(tParams["mode"]=="15s")then
		command = "s lcd on time 2"
	elseif(tParams["mode"]=="30s")then
		command = "s lcd on time 3"
	elseif(tParams["mode"]=="60s")then
		command = "s lcd on time 4"
	end
   PackAndQueueCommand("SetLcdOnTime",command)
end


function EX_CMD.SetOutputHDCP(tParams)
	local command = ""
	if(tParams["HDCP"]=="HDCP 1.4")then
		command = "s output "..tostring(tParams["outputPort"]).." hdcp 1"
	elseif(tParams["HDCP"]=="HDCP 2.2")then
		command = "s output "..tostring(tParams["outputPort"]).." hdcp 2"
	elseif(tParams["HDCP"]=="Follow sink")then
		command = "s output "..tostring(tParams["outputPort"]).." hdcp 3"
	elseif(tParams["HDCP"]=="Follow source")then
		command = "s output "..tostring(tParams["outputPort"]).." hdcp 4"
	elseif(tParams["HDCP"]=="USER MODE")then
		command = "s output "..tostring(tParams["outputPort"]).." hdcp 5"
	end
	PackAndQueueCommand("SetOutputHDCP",command)
end

function EX_CMD.SetOutputStreamMode(tParams)
    local command = ""
    if(tParams["mode"] ~= nil and tParams["mode"] == "On")then
		command = "s output ".. tostring(tParams["outputPort"]).." stream 1"
    elseif(tParams["mode"] ~= nil and tParams["mode"] == "Off")then
		command = "s output ".. tostring(tParams["outputPort"]).." stream 0"
    end
	PackAndQueueCommand("SetOutputStreamMode",command)
end

function EX_CMD.SetOutputVideoMode(tParams)
	local command = ""
	if(tParams["mode"]=="pass-through")then
		command = "s output ".. tostring(tParams["outputPort"]).." video mode 1"
	elseif(tParams["mode"]=="8k->4k")then
		command = "s output ".. tostring(tParams["outputPort"]).." video mode 2"
	elseif(tParams["mode"]=="8k/4k->1080p")then
		command = "s output ".. tostring(tParams["outputPort"]).." video mode 3"
	elseif(tParams["mode"]=="auto(follow sink EDID)")then
		command = "s output ".. tostring(tParams["outputPort"]).." video mode 4"
	elseif(tParams["mode"]=="audio only")then
		command = "s output ".. tostring(tParams["outputPort"]).." video mode 5"
	end
	PackAndQueueCommand("SetOutputVideoMode",command)
end

function EX_CMD.SetOutputHdrMode(tParams)
	local command = ""
	if(tParams["mode"]=="pass-through")then
		command = "s output ".. tostring(tParams["outputPort"]).." hdr 1"
	elseif(tParams["mode"]=="HDR to SDR")then
		command = "s output ".. tostring(tParams["outputPort"]).." hdr 2"
	elseif(tParams["mode"]=="auto(follow sink EDID)")then
		command = "s output ".. tostring(tParams["outputPort"]).." hdr 3"
	end
	PackAndQueueCommand("SetOutputHdrMode",command)
end

function EX_CMD.SetOutputArcMode(tParams)
    local command = ""
    if(tParams["mode"] ~= nil and tParams["mode"] == "On")then
		command = "s output ".. tostring(tParams["outputPort"]).." arc 1"
    elseif(tParams["mode"] ~= nil and tParams["mode"] == "Off")then
		command = "s output ".. tostring(tParams["outputPort"]).." arc 0"
    end
    PackAndQueueCommand("SetOutputArcMode",command)
end


function EX_CMD.SetOutputAudioMuteMode(tParams)
    local command = ""
    if(tParams["mode"] ~= nil and tParams["mode"] == "On")then
		command = "s output ".. tostring(tParams["outputPort"]).." audio mute 1"
    elseif(tParams["mode"] ~= nil and tParams["mode"] == "Off")then
		command = "s output ".. tostring(tParams["outputPort"]).." audio mute 0"
    end
    PackAndQueueCommand("SetOutputAudioMuteMode",command)
end


--[[
 * @Author      	Ws.Lf
 * @brief			Set the connected device output video switch
 * @param[tParams]	tParams["inputPort"]
					tParams["outputPort"]
 * @return			None
 * @Remark			None
--]]
function EX_CMD.SetVideoSwitch(tParams)
    local command = ""
    --LOG:Trace("tParams[inputPort] = "..tParams["inputPort"].." , tParams[outputPort] = " ..tParams["outputPort"])
	command = "s output "..tostring(tParams["outputPort"]).." in source "..tostring(tParams["inputPort"])
    --LOG:Trace("command = " .. command)
    PackAndQueueCommand("SetVideoSwitch",command)
end

function EX_CMD.SetOutputExaEnableOrDisable(tParams)
	local command = ""
	if(tParams["mode"]=="Enable")then
		command = "s output ".. tostring(tParams["outputPort"]).." exa 1"
	elseif(tParams["mode"]=="Disable")then
		command = "s output ".. tostring(tParams["outputPort"]).." exa 2"
	end
	PackAndQueueCommand("SetOutputExaEnableOrDisable",command)
end

function EX_CMD.SetOutputExaMode(tParams)
	local command = ""
	if(tParams["mode"]=="bind to input mode")then
		command = "s output exa mode 0"
	elseif(tParams["mode"]=="bind to output mode")then
		command = "s output exa mode 1"
	elseif(tParams["mode"]=="matrix mode")then
		command = "s output exa mode 2"
	end
	PackAndQueueCommand("SetOutputExaMode",command)
end

function EX_CMD.SetExaSource(tParams)
	local command = ""
	command = "s output "..tostring(tParams["ExaOutput"]).." exa in source "..tostring(tParams["inputPort"])
	PackAndQueueCommand("SetOutputExaEnableOrDisable",command)
end

--[[
 * @Author      	Ws.Lf
 * @brief			Set the connected device output hdmi stream mode
 * @param[tParams]	tParams["Preset"] Preset 1 Preset 2 ....Preset 8
					tParams["Mode"] Recall Save Clear Query
 * @return			None
 * @Remark			None
--]]
function EX_CMD.SetPresetFunction(tParams)
	local cmd,presetId
	--LogTrace("EX_CMD.SetPresetFunction")
	if(tParams["Preset"]=="Preset 1") then
		presetId = 1
	elseif(tParams["Preset"]=="Preset 2")then
		presetId = 2
	elseif(tParams["Preset"]=="Preset 3")then
		presetId = 3
	elseif(tParams["Preset"]=="Preset 4")then
		presetId = 4
	elseif(tParams["Preset"]=="Preset 5")then
		presetId = 5
	elseif(tParams["Preset"]=="Preset 6")then
		presetId = 6
	elseif(tParams["Preset"]=="Preset 7")then
		presetId = 7
	elseif(tParams["Preset"]=="Preset 8")then
		presetId = 8
	end

	if(tParams["Mode"]=="Recall")then
		cmd = "s recall preset "
	elseif(tParams["Mode"]=="Save")then
		cmd = "s save preset "
	elseif(tParams["Mode"]=="Clear")then
		cmd = "s clear preset "
	elseif(tParams["Mode"]=="Query")then
		cmd = "r preset "
	end
	cmd = cmd..presetId
    --LOG:Trace("command = " .. cmd)
    PackAndQueueCommand("SetPresetFunction",cmd)
end

--[[
 * @Author      	Ws.Lf
 * @brief			Set the connected device output hdmi stream mode
 * @param[tParams]	tParams["Preset"] Preset 1 Preset 2 ....Preset 8
					tParams["Mode"] Recall Save Clear Query
 * @return			None
 * @Remark			None
--]]
function EX_CMD.SetCECCommand(tParams)
	local cmd
	--LogTrace("EX_CMD.SetCECCommand")
	if(string.find(tParams["CECCommand"],"CEC IN Power On") ~= nil)then
		cmd = "s cec in "..tostring(tParams["port"]).." on"
	elseif(string.find(tParams["CECCommand"],"CEC IN Power Off") ~= nil)then
		cmd = "s cec in "..tostring(tParams["port"]).." off"
	elseif(string.find(tParams["CECCommand"],"CEC IN Menu") ~= nil)then
		cmd = "s cec in "..tostring(tParams["port"]).." menu"
	elseif(string.find(tParams["CECCommand"],"CEC IN Back") ~= nil)then
		cmd = "s cec in "..tostring(tParams["port"]).." back"
	elseif(string.find(tParams["CECCommand"],"CEC IN Left") ~= nil)then
		cmd = "s cec in "..tostring(tParams["port"]).." left"
	elseif(string.find(tParams["CECCommand"],"CEC IN Right") ~= nil)then
		cmd = "s cec in "..tostring(tParams["port"]).." right"
	elseif(string.find(tParams["CECCommand"],"CEC IN Up") ~= nil)then
		cmd = "s cec in "..tostring(tParams["port"]).." up"
	elseif(string.find(tParams["CECCommand"],"CEC IN Down") ~= nil)then
		cmd = "s cec in "..tostring(tParams["port"]).." down"
	elseif(string.find(tParams["CECCommand"],"CEC IN Enter") ~= nil)then
		cmd = "s cec in "..tostring(tParams["port"]).." enter"
	elseif(string.find(tParams["CECCommand"],"CEC IN Play") ~= nil)then
		cmd = "s cec in "..tostring(tParams["port"]).." play"
	elseif(string.find(tParams["CECCommand"],"CEC IN Pause") ~= nil)then
		cmd = "s cec in "..tostring(tParams["port"]).." pause"
	elseif(string.find(tParams["CECCommand"],"CEC IN Stop") ~= nil)then
		cmd = "s cec in "..tostring(tParams["port"]).." stop"
	elseif(string.find(tParams["CECCommand"],"CEC IN Rew") ~= nil)then
		cmd = "s cec in "..tostring(tParams["port"]).." rew"
	elseif(string.find(tParams["CECCommand"],"CEC IN Mute") ~= nil)then
		cmd = "s cec in "..tostring(tParams["port"]).." mute"
	elseif(string.find(tParams["CECCommand"],"CEC IN Vol Up") ~= nil)then
		cmd = "s cec in "..tostring(tParams["port"]).." vol+"
	elseif(string.find(tParams["CECCommand"],"CEC IN Vol Down") ~= nil)then
		cmd = "s cec in "..tostring(tParams["port"]).." vol-"
	elseif(string.find(tParams["CECCommand"],"CEC IN Fast Forward") ~= nil)then
		cmd = "s cec in "..tostring(tParams["port"]).." ff"
	elseif(string.find(tParams["CECCommand"],"CEC IN Previous") ~= nil)then
		cmd = "s cec in "..tostring(tParams["port"]).." previous"
	elseif(string.find(tParams["CECCommand"],"CEC IN Next") ~= nil)then
		cmd = "s cec in "..tostring(tParams["port"]).." next"
	elseif(string.find(tParams["CECCommand"],"CEC HDMI Out Power On") ~= nil)then
		cmd = "s cec hdmi out "..tostring(tParams["port"]).." on"
	elseif(string.find(tParams["CECCommand"],"CEC HDMI Out Power Off") ~= nil)then
		cmd = "s cec hdmi out "..tostring(tParams["port"]).." off"
	elseif(string.find(tParams["CECCommand"],"CEC HDMI Out Mute") ~= nil)then
		cmd = "s cec hdmi out "..tostring(tParams["port"]).." mute"
	elseif(string.find(tParams["CECCommand"],"CEC HDMI Out Vol Up") ~= nil)then
		cmd = "s cec hdmi out "..tostring(tParams["port"]).." vol+"
	elseif(string.find(tParams["CECCommand"],"CEC HDMI Out Vol Down") ~= nil)then
		cmd = "s cec hdmi out "..tostring(tParams["port"]).." vol-"
	elseif(string.find(tParams["CECCommand"],"CEC HDMI Out Active") ~= nil)then
		cmd = "s cec hdmi out "..tostring(tParams["port"]).." active"
	end
    --LOG:Trace("command = " .. cmd)
	PackAndQueueCommand("SetCECCommand",cmd)
end







 end)
package.preload['properties'] = (function (...)
--[[=============================================================================
    Properties Code

    Copyright 2015 Control4 Corporation. All Rights Reserved.
===============================================================================]]

-- This macro is utilized to identify the version string of the driver template version used.
if (TEMPLATE_VERSION ~= nil) then
	TEMPLATE_VERSION.properties = "2015.03.31"
end

function ON_PROPERTY_CHANGED.NetworkKeepAliveIntervalSeconds(propertyValue)
	gNetworkKeepAliveInterval = tonumber(propertyValue)

end

function ON_PROPERTY_CHANGED.RampingMethod(propertyValue)
    if (gInitializingDriver == true) then return end
    
    if (propertyValue == "Pulse Commands") then 
	   gAVSwitchProxy._UsePulseCommandsForVolumeRamping = true 
    else
	   gAVSwitchProxy._UsePulseCommandsForVolumeRamping = false
    end
    
end

function ON_PROPERTY_CHANGED.VolumeRampSteps(propertyValue)
    if (gInitializingDriver == true) then return end
    
    local minDeviceLevel = MIN_DEVICE_LEVEL
    local maxDeviceLevel = MAX_DEVICE_LEVEL
    tVolumeCurve = getVolumeCurve(minDeviceLevel, maxDeviceLevel)
    
end

function ON_PROPERTY_CHANGED.VolumeRampSlope(propertyValue)
    if (gInitializingDriver == true) then return end
    
    local minDeviceLevel = MIN_DEVICE_LEVEL
    local maxDeviceLevel = MAX_DEVICE_LEVEL
    tVolumeCurve = getVolumeCurve(minDeviceLevel, maxDeviceLevel)
    
end

--[[=============================================================================
    UpdateProperty(propertyName, propertyValue)
  
    Description:
    Sets the value of the given property in the driver
  
    Parameters:
    propertyName(string)  - The name of the property to change
    propertyValue(string) - The value of the property being changed
  
    Returns:
    None
===============================================================================]]
function UpdateProperty(propertyName, propertyValue)

	if (Properties[propertyName] ~= nil) then
		C4:UpdateProperty(propertyName, propertyValue)
	end
end

 end)
package.preload['proxy_commands'] = (function (...)
--[[=============================================================================
    Commands received from the AVSwitch proxy (ReceivedFromProxy)

    Copyright 2015 Control4 Corporation. All Rights Reserved.
===============================================================================]]

-- This macro is utilized to identify the version string of the driver template version used.
if (TEMPLATE_VERSION ~= nil) then
	TEMPLATE_VERSION.device_messages = "2015.03.31"
end

function CONNECT_OUTPUT(output, class, output_id)
    local command_delay = tonumber(Properties["Power On Delay Seconds"])
    local delay_units = "SECONDS"
    local command
    -- TODO: create packet/command to send to the device
    command = ""		--tPowerCommandMap[output] .. "01"
    --LogTrace("command = " .. command)
    --PackAndQueueCommand("CONNECT_OUTPUT", command, command_delay, delay_units)

    --local isAudio = (output_id >= 4000)
    --if (isAudio) then
	--   GetDeviceVolumeStatus(output)
    --end
end

function DISCONNECT_OUTPUT(output, class, output_id)
    local command_delay = tonumber(Properties["Power Off Delay Seconds"])
    local delay_units = "SECONDS"
    local command = ""
    --local isAudio = (output_id >= 4000)
   --[[In certain scenarios (based upon AV connections and project bindings), a DISCONNECT_OUTPUT command is sent in error by the proxy.
	   This code block utilized timers that are started in the SET_INPUT function to determine if this DISCONNECT_OUTPUT command is
	   associated with a reselection transaction, in whcih case we will abort...
    --]]
    --if not (isAudio) then
    --if (isAudioSelectionInProgress(output_id) == true) then
    --	  LogTrace("Audio Selection is in progress.  Not Disconnecting.")
    --	  return
    --   elseif (isHDMIAudioSelectionInProgress(output, output_id) == true) then
    --	  LogTrace("HDMI Audio Selection is in progress.  Not Disconnecting.")
    --      return
    --   end
    --end

	--   if (isAudio) then
	--	  gOutputToInputAudioMap[output] = -1
	--	  command = ""  	--audio disconnect element
	--   else
	--	  gOutputToInputMap[output] = -1
	--	  command = ""		--video disconnect element
	--   end
	   -- TODO: create packet/command to send to the device
	--   command = command .. "" 	--tOutputCommandMap[output]	--tPowerCommandMap[output]

	   -- TODO: If the device will automatically report power status after
	   --	the Off command is sent, then the line below can be commented out
	   --GetDevicePowerStatus(output)
    --LogTrace("command = " .. command)
    PackAndQueueCommand("DISCONNECT_OUTPUT", command, command_delay, delay_units)
end

--=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
-- Input Selection and AV Path Functions
--=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
function SET_INPUT(idBinding, output, input, input_id, class, output_id, bSwitchSeparate, bVideo, bAudio)
    LogTrace("")
    LogTrace("OUTPUT: " .. output .. "(" .. output_id .. ")")
    LogTrace("INPUT: " .. input .. "(" .. input_id .. ")")
    --LogTrace("AUDIO: " .. tostring(bAudio) .. " VIDEO: " .. tostring(bVideo))
    LogTrace("SWITCH SEPARATE: " .. tostring(bSwitchSeparate))
    LogTrace("")

    local command

    if(output_id < 3000) then --HDMI OUTPUT

		command = "s output " ..tOutputCommandMap[output].. " in source " ..tInputCommandMap[input]
	elseif(output_id < 5000 and output_id > 3999)then
		command = "s output "..tostring(output+1).." exa in source "..tAudioInputMap[input_id]
    end

    if (command == nil) then
	   LogTrace("command is nil")
    else
	   LogTrace("command = " .. command)
	   PackAndQueueCommand("SET_INPUT", command)
    end
end

--=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
-- Volume Control Functions
--=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
function MUTE_OFF(output)
	local command
	 command = tVolumeSetCommandMap[output] .. tVolumeLastMap[output]
	LogTrace("command = " .. command)
	PackAndQueueCommand("MUTE_OFF", command)
end

function MUTE_ON(output)
	local command
	 command = tVolumeSetCommandMap[output] .. "0"
	LogTrace("command = " .. command)
	PackAndQueueCommand("MUTE_ON", command)
end

function MUTE_TOGGLE(output)
	local command
	 if (tVolumeCurrentMap[output] == "0") then
	   MUTE_OFF(output)
	 else
	   MUTE_ON(output)
	 end
end

function SET_VOLUME_LEVEL(output, c4VolumeLevel)
	local minDeviceLevel = MIN_DEVICE_LEVEL
	local maxDeviceLevel = MAX_DEVICE_LEVEL
	local deviceVolumeLevel = ConvertVolumeToDevice(c4VolumeLevel, minDeviceLevel, maxDeviceLevel)
	local command = tVolumeSetCommandMap[output] .. deviceVolumeLevel
	LogTrace("command = " .. command)
	PackAndQueueCommand("SET_VOLUME_LEVEL", command)
end

function SET_VOLUME_LEVEL_DEVICE(output, deviceVolumeLevel)
	--Called from ContinueVolumeRamping()
	local command = tVolumeSetCommandMap[output] .. deviceVolumeLevel
	LogTrace("command = " .. command)
	local command_delay = tonumber(Properties["Volume Ramp Delay Milliseconds"])
	PackAndQueueCommand("SET_VOLUME_LEVEL_DEVICE", command, command_delay)
end

function PULSE_VOL_DOWN(output)
     local outputAsNum = tonumber(output)
	local command
	 if (tVolumeCurrentMap[output] == "0") then
	   command = tVolumeSetCommandMap[outputAsNum] .. (tonumber(tVolumeLastMap[outputAsNum]) - 1)
	 else
	   command = tVolumeSetCommandMap[outputAsNum] .. (tonumber(tVolumeCurrentMap[outputAsNum]) - 1)
	 end
	LogTrace("command = " .. command)
	local command_delay = tonumber(Properties["Volume Ramp Delay Milliseconds"])
	PackAndQueueCommand("PULSE_VOL_DOWN", command, command_delay)
end

function PULSE_VOL_UP(output)
     local outputAsNum = tonumber(output)
	local command
	 if (tVolumeCurrentMap[output] == "0") then
	   command = tVolumeSetCommandMap[outputAsNum] .. (tonumber(tVolumeLastMap[outputAsNum]) + 1)
	 else
	   command = tVolumeSetCommandMap[outputAsNum] .. (tonumber(tVolumeCurrentMap[outputAsNum]) + 1)
	 end
	LogTrace("command = " .. command)
	local command_delay = tonumber(Properties["Volume Ramp Delay Milliseconds"])
	PackAndQueueCommand("PULSE_VOL_UP", command, command_delay)
end

--=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
-- Helper Functions
--=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
function SEND_COMMAND_FROM_COMMAND_TABLE(idBinding, output, command_name)
    local output_for_log = output or "nil"
    LogTrace("SEND_COMMAND_FROM_COMMAND_TABLE(), idBinding=" .. idBinding .. ", output=" .. output_for_log .. ", command_name=" .. command_name)

	-- TODO: create packet/command to send to the device
	local command = GetCommandFromCommandTable(idBinding, output, command_name)

	if (command == nil) then
		LogTrace("command is nil")
	else
		LogTrace("command = " .. command)
		PackAndQueueCommand(command_name, command)
	end
end

function GetCommandFromCommandTable(idBinding, command_name)
	LogTrace("GetCommand()")
	local t = {}

	 t = CMDS

	if (t[idBinding] ~= nil) then
	   if (t[idBinding][command_name] ~= nil) then
		  return t[idBinding][command_name]
	   end
	end

	if (t[command_name] ~= nil) then
		return t[command_name]
	else
		LogWarn('GetCommandFromCommandTable: command not defined - '.. command_name)
		return nil
	end

end

function GetDeviceVolumeStatus(output)
    LOG:Trace("GetDeviceVolumeStatus(), output = " .. output)

	local command = tVolumeQueryMap[output]
	LOG:Trace("command = " .. command)
	PackAndQueueCommand("GetDeviceVolumeStatus: Volume", command)
end

function GetDevicePowerStatus(output)
    --LOG:Trace("GetDevicePowerStatus()")

	-- TODO: verify table entry in Volume in QUERY table
	--local command = tPowerCommandMap[output] -- .. "?"
	--LOG:Trace("command = " .. command)
	--PackAndQueueCommand("GetDevicePowerStatus: Volume", command)
end
 end)
package.preload['avswitch.avswitch_proxy_class'] = (function (...)
--[[=============================================================================
    AVSwitch Proxy Class Code

    Copyright 2015 Control4 Corporation. All Rights Reserved.
===============================================================================]]

-- This macro is utilized to identify the version string of the driver template version used.
if (TEMPLATE_VERSION ~= nil) then
	TEMPLATE_VERSION.properties = "2015.03.31"
end

AVSwitchProxy = inheritsFrom(nil)

function AVSwitchProxy:construct(avswitchBindingID, bProcessesDeviceMessages, tVolumeRampingTracking, bUsePulseCommandsForVolumeRamping)
	-- member variables
	self._AVSwitchBindingID = avswitchBindingID
	self._PowerState = {}						--Valid Values: "ON", "OFF", "POWER_ON_SEQUENCE", "POWER_OFF_SEQUENCE"
	self._VolumeIsRamping = false
	self._VolumeRamping = tVolumeRampingTracking		--[0] = {state = false,mode = "",} ||	"state" is boolean, "mode" values: "VOLUME_UP" & "VOLUME_DOWN"
	self._UsePulseCommandsForVolumeRamping = bUsePulseCommandsForVolumeRamping or false
	self._LastVolumeStatusValue = {}	
	self._MenuNavigationInProgress = false
     self._MenuNavigationMode = ""
	self._MenuNavigationProxyID = ""
	self._MenuNavigationOutput = ""
	self._CurrentlySelectedInput = {}
	self._PreviouslySelectedInput = {}
	self._ProcessesDeviceMessages = bProcessesDeviceMessages
	self._ControlMethod = ""						--Valid Values: "NETWORK", "SERIAL", "IR" 
end

------------------------------------------------------------------------
-- AVSwitch Proxy Commands (PRX_CMD)
------------------------------------------------------------------------
--=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
-- Power Functions
--=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
function AVSwitchProxy:prx_ON(tParams)
	--Handled by CONNECT_OUTPUT
	--ON()
end

function AVSwitchProxy:prx_OFF(tParams)
	--Handled by DISCONNECT_OUTPUT
	--OFF()
end

function AVSwitchProxy:prx_CONNECT_OUTPUT(tParams)
	local output = tonumber(tParams.OUTPUT) % 1000 
	local class = tParams.CLASS
	local output_id = tonumber(tParams["OUTPUT"])
	
	if (self._ProcessesDeviceMessages == false) then
		self._PowerState[output] = 'ON'
	else	
		self._PowerState[output] = 'POWER_ON_SEQUENCE'
	end	
	
	CONNECT_OUTPUT(output, class, output_id)
end

function AVSwitchProxy:prx_DISCONNECT_OUTPUT(tParams)
    local output = tonumber(tParams.OUTPUT) % 1000
    local class = tParams.CLASS
    local output_id = tonumber(tParams["OUTPUT"])
    if (self._ProcessesDeviceMessages == false) then
	   self._PowerState[output] = 'OFF'
    else	
	   self._PowerState[output] = 'POWER_OFF_SEQUENCE'
    end	
    DISCONNECT_OUTPUT(output, class, output_id)
  
    self._CurrentlySelectedInput[output] = -1
    self._PreviouslySelectedInput[output_id] = -1
    C4:SendToProxy(self._AVSwitchBindingID, 'INPUT_OUTPUT_CHANGED', {INPUT = -1, OUTPUT = 4000 + output})
    C4:SendToProxy(self._AVSwitchBindingID, 'INPUT_OUTPUT_CHANGED', {INPUT = -1, OUTPUT = 2000 + output})
end


--=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
-- Input Selection and AV Path Functions
--=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
function AVSwitchProxy:prx_SET_INPUT(idBinding, tParams)
	local input = tonumber(tParams["INPUT"] % 1000)
	local output = tonumber(tParams["OUTPUT"] % 1000)
	local input_id = tonumber(tParams["INPUT"])
	local class = tParams["CLASS"]
	local output_id = tonumber(tParams["OUTPUT"])
	local bSwitchSeparate, bVideo, bAudio = false, false, false
	local bSwitchSeparate = tParams["SWITCH_SEPARATE"]
	if (tParams["SWITCH_SEPARATE"] == "True") then bSwitchSeparate = true end
	if (tParams["VIDEO"] == "True") then bVideo = true end
	if (tParams["AUDIO"] == "True") then bAudio = true end
	self._CurrentlySelectedInput[output_id] = input_id
	SET_INPUT(idBinding, output, input, input_id, class, output_id, bSwitchSeparate, bVideo, bAudio)
	self._PreviouslySelectedInput[output_id] = input_id
end

function AVSwitchProxy:prx_BINDING_CHANGE_ACTION(idBinding, tParams)
    BINDING_CHANGE_ACTION(tParams)
end

function AVSwitchProxy:prx_IS_AV_OUTPUT_TO_INPUT_VALID(idBinding, tParams)
    return IS_AV_OUTPUT_TO_INPUT_VALID(tParams)
end

--=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
-- Volume Control Functions
--=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
function AVSwitchProxy:prx_MUTE_OFF(tParams)
	local output = tonumber(tParams["OUTPUT"] % 1000) or DEFAULT_OUTPUT_ID
	MUTE_OFF(output)
end

function AVSwitchProxy:prx_MUTE_ON(tParams)
	local output = tonumber(tParams["OUTPUT"] % 1000) or DEFAULT_OUTPUT_ID
	MUTE_ON(output)
end

function AVSwitchProxy:prx_MUTE_TOGGLE(tParams)
	local output = tonumber(tParams["OUTPUT"] % 1000) 
	MUTE_TOGGLE(output)
end

function AVSwitchProxy:prx_SET_VOLUME_LEVEL(tParams)
	local output = tonumber(tParams["OUTPUT"] % 1000) 
	local c4VolumeLevel = tonumber(tParams['LEVEL'])
	SET_VOLUME_LEVEL(output, c4VolumeLevel)
end

function AVSwitchProxy:prx_PULSE_VOL_DOWN(tParams)
	local output = tonumber(tParams["OUTPUT"] % 1000) 
	PULSE_VOL_DOWN(output)
end

function AVSwitchProxy:prx_PULSE_VOL_UP(tParams)
	local output = tonumber(tParams["OUTPUT"] % 1000) 
	PULSE_VOL_UP(output)
end

function AVSwitchProxy:prx_START_VOL_DOWN(tParams)
	local output = tonumber(tParams["OUTPUT"] % 1000) 
	self:ChangeVolume(output, "START_VOL_DOWN")
end

function AVSwitchProxy:prx_START_VOL_UP(tParams)
	local output = tonumber(tParams["OUTPUT"] % 1000)
	self:ChangeVolume(output, "START_VOL_UP")
end

function AVSwitchProxy:prx_STOP_VOL_DOWN(tParams)
	local output = tonumber(tParams["OUTPUT"] % 1000)
	self:ChangeVolume(output, "STOP_VOL_DOWN")
end

function AVSwitchProxy:prx_STOP_VOL_UP(tParams)
	local output = tonumber(tParams["OUTPUT"] % 1000)
	self:ChangeVolume(output, "STOP_VOL_UP")
end

function AVSwitchProxy:prx_PULSE_BASS_DOWN(tParams)
	local output = tonumber(tParams["OUTPUT"] % 1000) 
	PULSE_BASS_DOWN(output)
end

function AVSwitchProxy:prx_PULSE_BASS_UP(tParams)
	local output = tonumber(tParams["OUTPUT"] % 1000) 
	PULSE_BASS_UP(output)
end

function AVSwitchProxy:prx_SET_BASS_LEVEL(tParams)
	local output = tonumber(tParams["OUTPUT"] % 1000) 
	local c4BassLevel = tonumber(tParams['LEVEL'])
	SET_BASS_LEVEL(output, c4BassLevel)
end

function AVSwitchProxy:prx_PULSE_TREBLE_DOWN(tParams)
	local output = tonumber(tParams["OUTPUT"] % 1000) 
	PULSE_TREBLE_DOWN(output)
end

function AVSwitchProxy:prx_PULSE_TREBLE_UP(tParams)
	local output = tonumber(tParams["OUTPUT"] % 1000) 
	PULSE_TREBLE_UP(output)
end

function AVSwitchProxy:prx_SET_TREBLE_LEVEL(tParams)
	local output = tonumber(tParams["OUTPUT"] % 1000) 
	local c4TrebleLevel = tonumber(tParams['LEVEL'])
	SET_TREBLE_LEVEL(output, c4TrebleLevel)
end

---------------------- Volume Helper Functions ----------------------
function AVSwitchProxy:ChangeVolume(output, command_name)
	if (command_name == "STOP_VOL_UP") or (command_name == "STOP_VOL_DOWN") then
		self._VolumeIsRamping = false
		self._VolumeRamping[output].state = false
		self._VolumeRamping[output].mode = ""
	elseif (command_name == "START_VOL_UP") then 
		self._VolumeIsRamping = true
		self._VolumeRamping[output].state = true
		self._VolumeRamping[output].mode = "VOLUME_UP" 
		PULSE_VOL_UP(output)	
	elseif (command_name == "START_VOL_DOWN") then 	
		self._VolumeIsRamping = true
		self._VolumeRamping[output].state = true
		self._VolumeRamping[output].mode = "VOLUME_DOWN"	
		PULSE_VOL_DOWN(output)		
	else
		LogWarn(command_name .. " not handled in ChangeVolume()")
	end
end

function AVSwitchProxy:ContinueVolumeRamping(output)
	local command
	 if (self._UsePulseCommandsForVolumeRamping) then
		if (self._VolumeRamping[output].mode == "VOLUME_UP") then
		  PULSE_VOL_UP(output)	
		elseif (self._VolumeRamping[output].mode == "VOLUME_DOWN") then
		  PULSE_VOL_DOWN(output)	
		else
		  LogWarn("ContinueVolumeRamping() ramping mode is not valid.")
		end	
	 else
		local volume = self._LastVolumeStatusValue[output]
		local deviceVolumeLevel = self:GetNextVolumeCurveValue(output, volume)
		if (deviceVolumeLevel ~= nil) then
			self._LastVolumeStatusValue[output] = deviceVolumeLevel
			SET_VOLUME_LEVEL_DEVICE(output, deviceVolumeLevel)                                 
		else
			LogWarn("ContinueVolumeRamping() next value is nil")
			return
		end
	 end
end

function AVSwitchProxy:GetNextVolumeCurveValue(output, volume)
	local i, point
	volume=tonumber(volume)
	if (self._VolumeRamping[output].mode == "VOLUME_UP") then
		for i=1,table.maxn(tVolumeCurve) do
			point=tonumber(tVolumeCurve[i])
			if point > volume then		
				return tVolumeCurve[i]
			end
		end
	elseif (self._VolumeRamping[output].mode == "VOLUME_DOWN") then
		for i=table.maxn(tVolumeCurve),1,-1 do
			point=tonumber(tVolumeCurve[i])
			if point < volume then
				return tVolumeCurve[i]
			end
		end
	else
		LogWarn("Volume Ramping Mode not set for "  .. tOutputConnMapId2Name[output])
		return nil
	end 
end

function AVSwitchProxy:CreateVolumeCurve(steps, slope, minDeviceLevel, maxDeviceLevel)
    local curveV = {}
    curveV.__index = curveV

    function curveV:new(min, max, base)
	 local len = max-min
	 local logBase = math.log(base)
	 local baseM1 = base-1

	 local instance = {
	   min = min,
	   max = max,
	   len = len,
	   base = base,
	   logBase = logBase,
	   baseM1 = baseM1,
	   toNormal = function(x)
		return (x-min)/len
	   end,
	   fromNormal = function(x)
		return min+x*len
	   end,
	   value = function(x)
		return math.log(x*baseM1+1)/logBase
	   end,
	   invert = function(x)
		return (math.exp(x*logBase)-1)/baseM1
	   end
	 }
	 return setmetatable(instance, self)
    end

    function curveV:list(from, to, steps)
	 local fromI = self.invert(self.toNormal(from))
	 local toI = self.invert(self.toNormal(to))

	 for i = 1, steps do
	   --print(i, self.fromNormal(self.value(fromI+(i-1)*(toI-fromI)/(steps-1))))
	    print(i, math.floor(self.fromNormal(self.value(fromI+(i-1)*(toI-fromI)/(steps-1)))))
	 end
    end
    
    function curveV:create_curve(from, to, steps)
	 local fromI = self.invert(self.toNormal(from))
	 local toI = self.invert(self.toNormal(to))
	 
      local tCurve = {}
	 for i = 1, steps do
	   --print(i, self.fromNormal(self.value(fromI+(i-1)*(toI-fromI)/(steps-1))))
	   --print(i, math.floor(self.fromNormal(self.value(fromI+(i-1)*(toI-fromI)/(steps-1)))))
	    
	    local x = math.floor(self.fromNormal(self.value(fromI+(i-1)*(toI-fromI)/(steps-1))))
	    
	    if (has_value(tCurve, x) == false) then
		  table.insert(tCurve, x)
		  print(i, x)
	    end
	 end
	 
	 return tCurve
    end
    
    

    -- min, max, base of log (must be > 1), try some for the best results
    local a = curveV:new(minDeviceLevel, maxDeviceLevel, slope)

    -- from, to, steps
    --a:list(minDeviceLevel, maxDeviceLevel, steps)
    
    local t = a:create_curve(minDeviceLevel, maxDeviceLevel, steps)
    
    return t

end

function has_value(tab, val)
    for index, value in ipairs(tab) do
        if value == val then
            return true
        end
    end

    return false
end

function ConvertVolumeToC4(volume, minDeviceLevel, maxDeviceLevel)
	--to be used when converting a volume level from a device to a 
	--percentage value that can be used by C4 proxies
	--"volume" is the volume value from the device
	--"minDeviceLevel" & "maxDeviceLevel" are the minimum and maximum volume levels
	--as specified in the device protocol documentation
	return ProcessVolumeLevel(volume, minDeviceLevel, maxDeviceLevel, 0, 100)
end

function ConvertVolumeToDevice(volume, minDeviceLevel, maxDeviceLevel)
	--to be used when converting a volume level from a C4 proxy to a 
	--value that can be used by the device 
	--"volume" is the volume value from the C4 proxy
	--"minDeviceLevel" & "maxDeviceLevel" are the minimum and maximum volume levels
	--as specified in the device protocol documentation
	return ProcessVolumeLevel(volume, 0, 100, minDeviceLevel, maxDeviceLevel)
end

function ProcessVolumeLevel(volLevel, minVolLevel, maxVolLevel, minDeviceLevel, maxDeviceLevel)
	  local level = (volLevel-minVolLevel)/(maxVolLevel-minVolLevel)
	  --LogInfo("level = " .. level)
	  local vl=(level*(maxDeviceLevel-minDeviceLevel))+minDeviceLevel
	  --LogInfo("vl = " .. vl)
	  vl= tonumber_loc(("%.".."0".."f"):format(vl))
	  --LogInfo("vl new = " .. vl)
	  LogInfo("ProcessVolumeLevel(level in=" .. volLevel .. ", level out=" .. vl .. ")")
	  return vl
end

--=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
-- Menu Functions
--=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
function AVSwitchProxy:prx_INFO(idBinding, tParams)
	local output = get_output_with_nil_test(tParams["OUTPUT"])
	SEND_COMMAND_FROM_COMMAND_TABLE(idBinding, output, "INFO")
end

function AVSwitchProxy:prx_GUIDE(idBinding, tParams)
	local output = get_output_with_nil_test(tParams["OUTPUT"])
	SEND_COMMAND_FROM_COMMAND_TABLE(idBinding, output, "GUIDE")
end

function AVSwitchProxy:prx_MENU(idBinding, tParams)
	local output = get_output_with_nil_test(tParams["OUTPUT"])
	SEND_COMMAND_FROM_COMMAND_TABLE(idBinding, output, "MENU")
end

function AVSwitchProxy:prx_CANCEL(idBinding, tParams)
	local output = get_output_with_nil_test(tParams["OUTPUT"])
	SEND_COMMAND_FROM_COMMAND_TABLE(idBinding, output, "CANCEL")
end

function AVSwitchProxy:prx_UP(idBinding, tParams)
	local output = get_output_with_nil_test(tParams["OUTPUT"])
	SEND_COMMAND_FROM_COMMAND_TABLE(idBinding, output, "UP")
end

function AVSwitchProxy:prx_DOWN(idBinding, tParams)
	local output = get_output_with_nil_test(tParams["OUTPUT"])
	SEND_COMMAND_FROM_COMMAND_TABLE(idBinding, output, "DOWN")
end

function AVSwitchProxy:prx_LEFT(idBinding, tParams)
	local output = get_output_with_nil_test(tParams["OUTPUT"])
	SEND_COMMAND_FROM_COMMAND_TABLE(idBinding, output, "LEFT")
end

function AVSwitchProxy:prx_RIGHT(idBinding, tParams)
	local output = get_output_with_nil_test(tParams["OUTPUT"])
	SEND_COMMAND_FROM_COMMAND_TABLE(idBinding, output, "RIGHT")
end

function AVSwitchProxy:prx_START_DOWN(idBinding, tParams)
	local output = get_output_with_nil_test(tParams["OUTPUT"])
	self:NavigateMenu(idBinding, output, "START_DOWN")
end

function AVSwitchProxy:prx_START_UP(idBinding, tParams)
	local output = get_output_with_nil_test(tParams["OUTPUT"])
	self:NavigateMenu(idBinding, output,  "START_UP")
end

function AVSwitchProxy:prx_START_LEFT(idBinding, tParams)
	local output = get_output_with_nil_test(tParams["OUTPUT"])
	self:NavigateMenu(idBinding, output, "START_LEFT")
end

function AVSwitchProxy:prx_START_RIGHT(idBinding, tParams)
	local output = get_output_with_nil_test(tParams["OUTPUT"])
	self:NavigateMenu(idBinding, output, "START_RIGHT")
end

function AVSwitchProxy:prx_STOP_DOWN(idBinding, tParams)
	local output = get_output_with_nil_test(tParams["OUTPUT"])
	self:NavigateMenu(idBinding, output, "STOP_DOWN")
end

function AVSwitchProxy:prx_STOP_UP(idBinding, tParams)
	local output = get_output_with_nil_test(tParams["OUTPUT"])
	self:NavigateMenu(idBinding, output, "STOP_UP")
end

function AVSwitchProxy:prx_STOP_LEFT(idBinding, tParams)
	local output = get_output_with_nil_test(tParams["OUTPUT"])
	self:NavigateMenu(idBinding, output, "STOP_LEFT")
end

function AVSwitchProxy:prx_STOP_RIGHT(idBinding, tParams)
	local output = get_output_with_nil_test(tParams["OUTPUT"])
	self:NavigateMenu(idBinding, output, "STOP_RIGHT")
end

function AVSwitchProxy:prx_ENTER(idBinding, tParams)
	local output = get_output_with_nil_test(tParams["OUTPUT"])
	SEND_COMMAND_FROM_COMMAND_TABLE(idBinding, output, "ENTER")
end

function AVSwitchProxy:prx_RECALL(idBinding, tParams)
	local output = get_output_with_nil_test(tParams["OUTPUT"])
	SEND_COMMAND_FROM_COMMAND_TABLE(idBinding, output, "RECALL")
end

function AVSwitchProxy:prx_OPEN_CLOSE(idBinding, tParams)
	local output = get_output_with_nil_test(tParams["OUTPUT"])
	SEND_COMMAND_FROM_COMMAND_TABLE(idBinding, output, "OPEN_CLOSE")
end

function AVSwitchProxy:prx_PROGRAM_A(idBinding, tParams)
	local output = get_output_with_nil_test(tParams["OUTPUT"])
	SEND_COMMAND_FROM_COMMAND_TABLE(idBinding, output, "PROGRAM_A")
end

function AVSwitchProxy:prx_PROGRAM_B(idBinding, tParams)
	local output = get_output_with_nil_test(tParams["OUTPUT"])
	SEND_COMMAND_FROM_COMMAND_TABLE(idBinding, output, "PROGRAM_B")
end

function AVSwitchProxy:prx_PROGRAM_C(idBinding, tParams)
	local output = get_output_with_nil_test(tParams["OUTPUT"])
	SEND_COMMAND_FROM_COMMAND_TABLE(idBinding, output, "PROGRAM_C")
end

function AVSwitchProxy:prx_PROGRAM_D(idBinding, tParams)
	local output = get_output_with_nil_test(tParams["OUTPUT"])
	SEND_COMMAND_FROM_COMMAND_TABLE(idBinding, output, "PROGRAM_D")
end

---------------------- Menu Navigation Helper Functions ----------------------
function AVSwitchProxy:NavigateMenu(idBinding, output, command_name)
	if (command_name == "STOP_UP") 
				or (command_name == "STOP_DOWN") 
				or (command_name == "STOP_LEFT") 
				or (command_name == "STOP_RIGHT") then
		self._MenuNavigationInProgress = false
		self._MenuNavigationMode = ""
		self._MenuNavigationProxyID = ""
		return
	elseif (command_name == "START_UP") then 
		self._MenuNavigationMode = "UP"
	elseif (command_name == "START_DOWN") then 	
		self._MenuNavigationMode = "DOWN"	
	elseif (command_name == "START_LEFT") then 
		self._MenuNavigationMode = "LEFT"	
     elseif (command_name == "START_RIGHT") then 
		self._MenuNavigationMode = "RIGHT"
	else
		LogWarn(command_name .. " not handled in NavigateMenu()")
	end
	
	SEND_COMMAND_FROM_COMMAND_TABLE(idBinding, output, self._MenuNavigationMode)
	self._MenuNavigationInProgress = true
	self._MenuNavigationProxyID = idBinding
	self._MenuNavigationOutput = output
	
end

--=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
-- Digit Functions
--=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
function AVSwitchProxy:prx_NUMBER_0(idBinding, tParams)
	local output = get_output_with_nil_test(tParams["OUTPUT"])
	SEND_COMMAND_FROM_COMMAND_TABLE(idBinding, output, "NUMBER_0")
end

function AVSwitchProxy:prx_NUMBER_1(idBinding, tParams)
	local output = get_output_with_nil_test(tParams["OUTPUT"])
	SEND_COMMAND_FROM_COMMAND_TABLE(idBinding, output, "NUMBER_1")
end

function AVSwitchProxy:prx_NUMBER_2(idBinding, tParams)
	local output = get_output_with_nil_test(tParams["OUTPUT"])
	SEND_COMMAND_FROM_COMMAND_TABLE(idBinding, output, "NUMBER_2")
end

function AVSwitchProxy:prx_NUMBER_3(idBinding, tParams)
	local output = get_output_with_nil_test(tParams["OUTPUT"])
	SEND_COMMAND_FROM_COMMAND_TABLE(idBinding, output, "NUMBER_3")
end

function AVSwitchProxy:prx_NUMBER_4(idBinding, tParams)
	local output = get_output_with_nil_test(tParams["OUTPUT"])
	SEND_COMMAND_FROM_COMMAND_TABLE(idBinding, output, "NUMBER_4")
end

function AVSwitchProxy:prx_NUMBER_5(idBinding, tParams)
	local output = get_output_with_nil_test(tParams["OUTPUT"])
	SEND_COMMAND_FROM_COMMAND_TABLE(idBinding, output, "NUMBER_5")
end

function AVSwitchProxy:prx_NUMBER_6(idBinding, tParams)
	local output = get_output_with_nil_test(tParams["OUTPUT"])
	SEND_COMMAND_FROM_COMMAND_TABLE(idBinding, output, "NUMBER_6")
end

function AVSwitchProxy:prx_NUMBER_7(idBinding, tParams)
	local output = get_output_with_nil_test(tParams["OUTPUT"])
	SEND_COMMAND_FROM_COMMAND_TABLE(idBinding, output, "NUMBER_7")
end

function AVSwitchProxy:prx_NUMBER_8(idBinding, tParams)
	local output = get_output_with_nil_test(tParams["OUTPUT"])
	SEND_COMMAND_FROM_COMMAND_TABLE(idBinding, output, "NUMBER_8")
end

function AVSwitchProxy:prx_NUMBER_9(idBinding, tParams)
	local output = get_output_with_nil_test(tParams["OUTPUT"])
	SEND_COMMAND_FROM_COMMAND_TABLE(idBinding, output, "NUMBER_9")
end

function AVSwitchProxy:prx_STAR(idBinding, tParams)
	local output = get_output_with_nil_test(tParams["OUTPUT"])
	SEND_COMMAND_FROM_COMMAND_TABLE(idBinding, output, "STAR")
end

function AVSwitchProxy:prx_POUND(idBinding, tParams)
	local output = get_output_with_nil_test(tParams["OUTPUT"])
	SEND_COMMAND_FROM_COMMAND_TABLE(idBinding, output, "POUND")
end

function get_output_with_nil_test(output)
	local id = nil
	if (output ~= nil) then
		id = tonumber(output % 1000)
	end
	return id
end

------------------------------------------------------------------------
-- AVSwitch Proxy Notifies
------------------------------------------------------------------------

function AVSwitchProxy:dev_InputOutputChanged(input_id, output_id)
	NOTIFY.INPUT_OUTPUT_CHANGED(self._AVSwitchBindingID, input_id, output_id)
end

function AVSwitchProxy:dev_PowerOn(output)
	self._PowerState[output] = "ON"
	NOTIFY.ON()	
end

function AVSwitchProxy:dev_PowerOff(output)
	self._PowerState[output] = "OFF"
	NOTIFY.OFF()
end

function AVSwitchProxy:dev_VolumeLevelChanged(output, c4Level, deviceLevel)
	NOTIFY.VOLUME_LEVEL_CHANGED(self._AVSwitchBindingID, output, c4Level)	
	
	if (self._VolumeIsRamping) then
		--do nothing
		--during volume ramping, LastVolumeStatusValue is set in ContinueVolumeRamping()
	else
		self._LastVolumeStatusValue[output] = deviceLevel
	end	
end

function AVSwitchProxy:dev_MuteChanged(output, state)
	NOTIFY.MUTE_CHANGED(self._AVSwitchBindingID, output, state)
end		

function AVSwitchProxy:dev_BassLevelChanged(output, level)
	NOTIFY.BASS_LEVEL_CHANGED(self._AVSwitchBindingID, output, level)
end	

function AVSwitchProxy:dev_TrebleLevelChanged(output, level)
	NOTIFY.TREBLE_LEVEL_CHANGED(self._AVSwitchBindingID, output, level)
end	

function AVSwitchProxy:dev_BalanceLevelChanged(output, level)
	NOTIFY.BALANCE_LEVEL_CHANGED(self._AVSwitchBindingID, output, level)
end	

function AVSwitchProxy:dev_LoudnessChanged(output, state)
	NOTIFY.LOUDNESS_CHANGED(self._AVSwitchBindingID, output, state)
end
 end)
--[[=============================================================================
    Basic Template for AVSwitch Driver

    Copyright 2015 Control4 Corporation. All Rights Reserved.
===============================================================================]]------------
require "common.c4_driver_declarations"
require "common.c4_common"
require "common.c4_init"
require "common.c4_property"
require "common.c4_command"
require "common.c4_notify"
require "common.c4_network_connection"
require "common.c4_serial_connection"
require "common.c4_ir_connection"
require "common.c4_utils"
require "lib.c4_timer"
require "actions"
require "device_specific_commands"
require "device_messages"
require "avswitch_init"
require "properties"
require "proxy_commands"
require "connections"
require "avswitch.avswitch_proxy_class"
require "avswitch.avswitch_proxy_commands"
require "avswitch.avswitch_proxy_notifies"
require "av_path"


-- This macro is utilized to identify the version string of the driver template version used.
if (TEMPLATE_VERSION ~= nil) then
	TEMPLATE_VERSION.driver = "2015.03.31"
end

--[[=============================================================================
    Constants
===============================================================================]]
AVSWITCH_PROXY_BINDINGID = 5001

--[[
    Device Volume Range
    TODO: edit "MIN_DEVICE_LEVEL" & "MAX_DEVICE_LEVEL" values based upon the protocol specification for volume range.
    If zones have volume ranges that vary, convert these constants into a table indexed by the mod value of the output connection
    and then update all references to handle the table structure.
--]]
MIN_DEVICE_LEVEL = 0
MAX_DEVICE_LEVEL = 100


--[[=============================================================================
    Initialization Code
===============================================================================]]
function ON_DRIVER_EARLY_INIT.main()

end

function ON_DRIVER_INIT.main()

	-- TODO: If cloud based driver then uncomment the following line
	--ConnectURL()
end

function ON_DRIVER_LATEINIT.main()
    C4:urlSetTimeout (20)
    DRIVER_NAME = C4:GetDriverConfigInfo("name")

	SetLogName(DRIVER_NAME)
end

function ON_DRIVER_EARLY_INIT.avswitch_driver()

end

function ON_DRIVER_INIT.avswitch_driver()


    -- Create an instance of the AVSwitchProxy class
    -- TODO: Change bProcessesDeviceMessages to false if Device Messages will not be processes
    local  bProcessesDeviceMessages = true
    local bUsePulseCommandsForVolumeRamping = false
    if (Properties["Ramping Method"] == "Pulse Commands") then bUsePulseCommandsForVolumeRamping = true end
    gAVSwitchProxy = AVSwitchProxy:new(AVSWITCH_PROXY_BINDINGID, bProcessesDeviceMessages, tVolumeRamping, bUsePulseCommandsForVolumeRamping)

    local minDeviceLevel = MIN_DEVICE_LEVEL
    local maxDeviceLevel = MAX_DEVICE_LEVEL
    tVolumeCurve = getVolumeCurve(minDeviceLevel, maxDeviceLevel)

	--[[
	For the "Volume Curve" method, tVolumeCurve is used to store volume level values that will be used to build volume commands during volume ramping. Specifically, they are used in GetNextVolumeCurveValue() which is called from the ContinueVolumeRamping() function.  Property values for "Volume Ramping Steps" and "Volume Ramping Slope" can be adjusted to get a smooth volume ramping from low to high volume.
	--]]
end

function getVolumeCurve(minDeviceLevel, maxDeviceLevel)
    local steps = tonumber(Properties["Volume Ramp Steps"])
    local slope = tonumber(Properties["Volume Ramp Slope"])
    local tCurve = gAVSwitchProxy:CreateVolumeCurve(steps, slope, minDeviceLevel, maxDeviceLevel)

    return tCurve
end

--[[=============================================================================
    Driver Code
===============================================================================]]
function PackAndQueueCommand(...)
--Multiple parameters 1.command name 2.command 3.command delay times 4.delay units
    local command_name = select(1, ...) or ""
    local command = select(2, ...) or ""
    local command_delay = select(3, ...) or tonumber(Properties["Command Delay Milliseconds"])
    local delay_units = select(4, ...) or "MILLISECONDS"

    LogTrace("PackAndQueueCommand(), command_name = " .. command_name .. ", command delay set to " .. command_delay .. " " .. delay_units)
    if (command == "") then
	   LogWarn("PackAndQueueCommand(), command_name = " .. command_name .. ", command string is empty - exiting PackAndQueueCommand()")
	   return
    end

    local cmd, stx, etx
    if (gControlMethod == "Network") then
		stx = ""
		etx = "!\r\n"
		cmd = stx .. command .. etx
    elseif (gControlMethod == "Serial") then
		stx = ""
		etx = "!\r\n"
		cmd = stx .. command .. etx
    else
		LogWarn("PackAndQueueCommand(): gControlMethod is not valid, ".. gControlMethod)
		return
    end
	LogTrace("PackAndQueueCommand(): [gControlMethod]"..gControlMethod.."[command name]"..command_name.." [command] "..command)
    gCon:QueueCommand(cmd, command_delay, delay_units, command_name)

end
