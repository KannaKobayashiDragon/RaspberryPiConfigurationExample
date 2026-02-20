#!/usr/bin/env python3

"""
+============================================================================================================+
| Bluetooth HID Server                                                                                       |
| - Raspberry Pi Zero 2 W - Bluetooth Classic RFCOMM Server with USB HID Keyboard Emulation and GPIO Auditing|
|                                                                                                            |
| Instructions:                                                                                              |
| 1. Stakced Hardwawre Auditing Logic (LEDs/Buzzer)                                                          |
| 2. Stacked HID Auditing Logic (Arrow Logic)                                                                |
| 3. Stacked HID Keyboard Logic (BIOS Compatible)                                                            |
|     - HOME + Arrow Keys + Delete/Backspace Support                                                         |
| 4. Stacked HID Deletion Logic (Delecting Rows in BIOS)                                                     |
+============================================================================================================+
"""

" Python Imports "
import bluetooth
import time
import sys
import signal
import traceback
import os
import json
import fcntl
from decimal import Decimal

# Import GPIOZero into LED & Buzzer Instance (Direct Call in Future)
# GPIOZero Has LED Library and Buzzer Library. Direct Call and Use.
from gpiozero import LED, Buzzer

"""
+============================================================================================================+
| GPIO Hardware Handler                                                                                      |
| Handle Physical Hardware Audit Signals - LEDs and Buzzer                                                   |                          
+============================================================================================================+
"""
class Hardware:
    """Hardware Class Object Initialization"""
    def __init__(Self) :
        # GPIO Mapping Based on Raspberry Pi Zero 2 W Board Layout
        # GND  : Physical PIN 6  
        # GPIOs :
            # GPIO27 : Physical PIN13
            # GPIO23 : Physical PIN16
            # GPIO24 : Physical PIN18
            # GPIO25 : Physical PIN22
            # GPIO26 : Physical PIN37

        # Attrib Initialization

        # LEDs GPIO Settings
        # Read and understand as "gpiozero(23)". 
        Self.LEDs = {
            "Red":LED(23), 
            "Yellow":LED(25),
            "Blue":LED(24),
            "White":LED(26)
        }

        # Buzzer GPIO Settings
        # Read and understand as "gpiozero(27)". 
        Self.Buzzer = Buzzer(27)

    # Hardware Runner
    # self.hw.run("LED", {"Color": "RED", "Duration": 1.0})
    # self.hw.run("BEEP", {"Command": "BEEP", "Parameters": {"Repeat": 2, "Pattern": "Short"}})
    # self.hw.run("BEEP", {"Command": "BEEP", "Parameters": {"Repeat": 2, "Pattern": "Long"}})
    # self.hw.run("SLEEP", {"Command": "WAIT", "Parameters": {"Seconds": 1.0}})
    
    def Run(Self, Command, Parameters):
        """GPIO Hardware Executor"""
        # Python Define
        # '2.0' is Abnormal Payload Handling
        DEFAULT_LED_SLEEP_TIME = 2.0 
        DEFAULT_LED_COLOR = "White"
        DEFAULT_BUZZER_OCCUR = 1
        DEFAULT_BUZZER_LAST = 2.0
        DEFAULT_SLEEP_TIME = 2.0

        # Try Execute Logic 
        try:
            
            # LED : First Parameter Handling (GPIO:Led)
            if Command == "LED":
                # Python_Dictionary.get(key, default_value)
                Toggling = Self.LEDs.get(Parameters.get("Color", DEFAULT_LED_COLOR))
                # Toggling - Not Empty Executor
                if Toggling:
                    # GPIO ON Logic
                    Toggling.on()
                    # Python_Dictionary.get(key, default_value)
                    # Default Sleep Value
                    time.sleep(float(Parameters.get("Duration", DEFAULT_LED_SLEEP_TIME)))
                    # GPIO OFF Logic
                    Toggling.off()
            
            # BEEP : First Parameter Handling (GPIO:Buzzer)
            elif Command == "BEEP":
                for Iteration in range(int(Parameters.get("Repeat", DEFAULT_BUZZER_OCCUR))):
                    # GPIO ON Logic
                    Self.Buzzer.on()
                    # Sleep Condition
                    if Parameters.get("Pattern") == "Short":
                        duration = 0.1
                    elif Parameters.get("Pattern") == "Long" :
                        duration = 0.5
                    else : 
                        duration = DEFAULT_BUZZER_LAST
                    # Sleep Logic
                    time.sleep(duration)
                    # GPIO OFF Logic
                    Self.Buzzer.off()

            # WAIT : First Parameter Handling (Sleep)
            elif Command == "WAIT":
                time.sleep(float(Parameters.get("Seconds", DEFAULT_SLEEP_TIME)))

        # Exception Error Handling
        except Exception as Error:
            print(f"[Hardware_Class] Failed To Execute {Command}: {Error}")

"""
+============================================================================================================+
| RaspberryKeyboard Class                                                                                    |
| Handle HID Emulation Logic - BIOS Compatible                                                               |
+============================================================================================================+
"""
class RaspberryKeyboard:

    #Python Define 
    # Modifier Key Bit Flags
    MOD_NONE = 0x00
    MOD_LCTRL = 0x01
    MOD_LSHIFT = 0x02
    MOD_LALT = 0x04
    # Windows/Command Key
    MOD_LGUI = 0x08      
    MOD_RCTRL = 0x10
    MOD_RSHIFT = 0x20
    MOD_RALT = 0x40
    MOD_RGUI = 0x80

    def __init__(Self, Test_Mode=False):
        #Python Define 
        # HID Device Path
        HID_DEVICE_PATH = '/dev/hidg0'
        
        # Attrib Initialization
        Self.Device = HID_DEVICE_PATH 
        Self.Debug = False
        # If Test_Mode True, Skip Actual HID Writes
        Self.Test_Mode = Test_Mode  
        Self.Last_Char = None
        Self.Last_Nodifier = 0
        # File Descriptor For Non-Blocking Writes
        Self.HID_FD = None  

        # Character Map with Arrow Keys and Special Keys
        Self.Char_map = {
            # Lowercase Letters
            'a': (0x04, 0), 'b': (0x05, 0), 'c': (0x06, 0), 'd': (0x07, 0), 'e': (0x08, 0),
            'f': (0x09, 0), 'g': (0x0a, 0), 'h': (0x0b, 0), 'i': (0x0c, 0), 'j': (0x0d, 0),
            'k': (0x0e, 0), 'l': (0x0f, 0), 'm': (0x10, 0), 'n': (0x11, 0), 'o': (0x12, 0),
            'p': (0x13, 0), 'q': (0x14, 0), 'r': (0x15, 0), 's': (0x16, 0), 't': (0x17, 0),
            'u': (0x18, 0), 'v': (0x19, 0), 'w': (0x1a, 0), 'x': (0x1b, 0), 'y': (0x1c, 0),
            'z': (0x1d, 0),

            # Uppercase letters (with Left Shift modifier = 0x02)
            'A': (0x04, 0x02), 'B': (0x05, 0x02), 'C': (0x06, 0x02), 'D': (0x07, 0x02), 'E': (0x08, 0x02),
            'F': (0x09, 0x02), 'G': (0x0a, 0x02), 'H': (0x0b, 0x02), 'I': (0x0c, 0x02), 'J': (0x0d, 0x02),
            'K': (0x0e, 0x02), 'L': (0x0f, 0x02), 'M': (0x10, 0x02), 'N': (0x11, 0x02), 'O': (0x12, 0x02),
            'P': (0x13, 0x02), 'Q': (0x14, 0x02), 'R': (0x15, 0x02), 'S': (0x16, 0x02), 'T': (0x17, 0x02),
            'U': (0x18, 0x02), 'V': (0x19, 0x02), 'W': (0x1a, 0x02), 'X': (0x1b, 0x02), 'Y': (0x1c, 0x02),
            'Z': (0x1d, 0x02),

            # Numbers
            '1': (0x1e, 0), '2': (0x1f, 0), '3': (0x20, 0), '4': (0x21, 0), '5': (0x22, 0),
            '6': (0x23, 0), '7': (0x24, 0), '8': (0x25, 0), '9': (0x26, 0), '0': (0x27, 0),

            # Special Characters
            ' ': (0x2c, 0),       # Space
            '\n': (0x28, 0),      # Enter
            '\t': (0x2b, 0),      # Tab
            '-': (0x2d, 0),       # Minus
            '=': (0x2e, 0),       # Equals
            '[': (0x2f, 0),       # Left bracket
            ']': (0x30, 0),       # Right bracket
            '\\': (0x31, 0),      # Backslash
            ';': (0x33, 0),       # Semicolon
            "'": (0x34, 0),       # Apostrophe
            '`': (0x35, 0),       # Grave accent
            ',': (0x36, 0),       # Comma
            '.': (0x37, 0),       # Period
            '/': (0x38, 0),       # Forward slash

            # Shifted Special Characters
            '!': (0x1e, 0x02), '@': (0x1f, 0x02), '#': (0x20, 0x02), '$': (0x21, 0x02), '%': (0x22, 0x02),
            '^': (0x23, 0x02), '&': (0x24, 0x02), '*': (0x25, 0x02), '(': (0x26, 0x02), ')': (0x27, 0x02),
            '_': (0x2d, 0x02), '+': (0x2e, 0x02), '{': (0x2f, 0x02), '}': (0x30, 0x02), '|': (0x31, 0x02),
            ':': (0x33, 0x02), '"': (0x34, 0x02), '~': (0x35, 0x02), '<': (0x36, 0x02), '>': (0x37, 0x02),
            '?': (0x38, 0x02),

            # ============== ARROW KEYS ==============
            'UP': (0x52, 0),       # Up Arrow
            'DOWN': (0x51, 0),     # Down Arrow
            'LEFT': (0x50, 0),     # Left Arrow
            'RIGHT': (0x4f, 0),    # Right Arrow

            # ============== NAVIGATION KEYS ==============
            'DELETE': (0x4c, 0),      # Delete (forward delete)
            'DEL': (0x4c, 0),         # Delete (alias)
            'BACKSPACE': (0x2a, 0),   # Backspace
            'HOME': (0x4a, 0),        # Home
            'END': (0x4d, 0),         # End
            'PAGEUP': (0x4b, 0),      # Page Up
            'PAGEDOWN': (0x4e, 0),    # Page Down
            'INSERT': (0x49, 0),      # Insert
            'ESCAPE': (0x29, 0),      # Escape
            'ESC': (0x29, 0),         # Escape (alias)
            'ENTER': (0x28, 0),       # Enter
            'RETURN': (0x28, 0),      # Enter (alias)
            'TAB': (0x2b, 0),         # Tab
            'SPACE': (0x2c, 0),       # Space

            # ============== FUNCTION KEYS ==============
            'F1': (0x3a, 0), 'F2': (0x3b, 0), 'F3': (0x3c, 0), 'F4': (0x3d, 0),
            'F5': (0x3e, 0), 'F6': (0x3f, 0), 'F7': (0x40, 0), 'F8': (0x41, 0),
            'F9': (0x42, 0), 'F10': (0x43, 0), 'F11': (0x44, 0), 'F12': (0x45, 0),

            # ============== LOCK KEYS ==============
            'CAPSLOCK': (0x39, 0),
            'NUMLOCK': (0x53, 0),
            'SCROLLLOCK': (0x47, 0),
        }

    def Open_HID_Device(Self):
        """Open HID Device With Non-Blocking Mode"""
        if Self.Test_Mode:
            return True
        try:
            if Self.HID_FD is None:
                # The "Rules" for how to talk to it (Bit Writing : O_WRONLY-Write-Only OR(Human Readable is AND) O_NONBLOCK-Non-Block(Do not Freeze This Running Program) ).
                # Old Logic : Self.HID_FD = os.open(Self.Device, os.O_WRONLY | os.O_NONBLOCK)
                # New Logic Reason : BIOS Password need Accuracy, not Fast-Response as delivered in NONBLOCK mode.
                Self.HID_FD = os.open(Self.Device, os.O_WRONLY)
            return True
        except Exception as e:
            print(f"[RaspberryKeyboard_Func_Open_Hid_Device] Failed to open {Self.Device}: {e}")
            return False


    def Close_HID_Device(Self):
        """Close HID Device"""
        # Close The File Descriptor and Reset The Variable
        if Self.HID_FD is not None:
            try:
                os.close(Self.HID_FD)
            except:
                # Ignore Errors If The Device Already Closed Or Gone
                pass
            Self.HID_FD = None

    def Type_Raw_Report(Self, Report, Max_Retries=5):
        """Writes Raw 8-Byte(Keystrokes) Reports To The HID Device With Retry Logic"""
        if Self.Test_Mode:
            print(f"[TEST_MODE] Send : {Report.hex()}")
            return True

        for Attempt_Iteration in range(Max_Retries):
            try:
                # Reopen Device If Needed
                if Self.HID_FD is None:
                    Self.HID_FD = os.open(Self.Device, os.O_WRONLY)

                # Write to Pipe
                os.write(Self.HID_FD, Report)
                return True

            except BlockingIOError:
                # Buffer Full, Wait And Retry
                time.sleep(0.05)
                print(f"[RaspberryKeyboard_Func_Type_Raw_Report] Buffer Full Triggered]")
                continue

            except OSError as Error:
                # EAGAIN (Error 11): Resource Temporarily Unavailable (Blocked).
                # In Non-Blocking Mode, This Means The Buffer Full ; Wait & Try Again.
                if Error.errno == 11:  
                    time.sleep(0.05)
                    continue
                # ESHUTDOWN (Error 108): Cannot Send After Transport Endpoint Shutdown.
                # Usually The USB Cable Unplugged / Driver Crashed.
                elif Error.errno == 108:
                    # Reopen The Device
                    Self.Close_HID_Device()
                    time.sleep(0.1)
                    try:
                        Self.HID_FD = os.open(Self.Device, os.O_WRONLY)
                    except:
                        pass
                    continue
                else:
                    # Unknown Error Handler
                    print(f"[Type_Raw_Report] HID_ERROR - OSError : {Error.errno}: {Error}")
                    return False
            except Exception as Error:
                print(f"[Type_Raw_Report] Attempt {Attempt_Iteration} - Error : {Error}")
                return False

        print(f"[Type_Raw_Report] HID Error - Failed After {Max_Retries} Retries")
        return False

    def Send_Key_With_Modifier(Self, Scan_Code, Modifier=0x00):
        """Send A Key Press(Scan_Code) With Optional Modifier"""

        try:
            # Press
            Keystroke = bytes([Modifier, 0, Scan_Code, 0, 0, 0, 0, 0])
            if not Self.Type_Raw_Report(Keystroke):
                return False
             # Slightly longer delay for BIOS Compatibility
            time.sleep(0.03) 

            # Release (All 0)
            if not Self.Type_Raw_Report(bytes([0]*8)):
                return False
            time.sleep(0.03)

            return True
        
        except Exception as Error:
            print(f"[Send_Key_With_Modifier] Send Modifier Modified Keystroke : {e}")
            return False

    def Type_Key(Self, Key_Name):
        """ Press Key By Name """

        # If Passes None or Empty String
        if not Key_Name:
            return False    
        
        # Key String Uppercase Handler & Handle "Words" vs "Single Characters"
        # This is used to Filter the Non-(Modified)-String : Because > 1 is not Single Key.
        if len(Key_Name) > 1: 
            Key_Search = Key_Name.upper() 
        # This is the Proper Bind Search (All Above Codes are Used for Condition Filtering to Reach Here)
        else:
            Key_Search = Key_Name

        # Search in Char_map
        # Valid "Words"
        if Key_Search in Self.Char_map:
            Scan_Code, Modifier = Self.Char_map[Key_Search]
        # Fallback : "Single Characters with Modifier"
        elif Key_Name in Self.Char_map:
            Scan_Code, Modifier = Self.Char_map[Key_Name]

        # Fallback : Error Handler
        else:
            # Key_Name and Key_Search are not In The Dictionary
            if Self.Debug:
                # ord() Check Invisible Characters Like Spaces Or Newlines.
                print(f"[HID_DEBUG] Unknown Key Found: '{Key_Name}' (ord={[ord(Character) for Character in Key_Name]})")
            return False

        # Success: Send The Report Hardware Pipe (HID_FD)
        return Self.Send_Key_With_Modifier(Scan_Code, Modifier)

    def Type_Char(Self, Char):
        """Type A Single Character"""

        # If Passes None or Empty String 
        if Char is None or len(Char) == 0:
            return False
        
        # Skip Control Characters And Non-Printable Chars
        # All ord Unicode Char < 32  are Control Characters (Non-Printable)
        if ord(Char) < 32 and Char not in ['\n', '\t']:
            return False
        
        return Self.Type_Key(Char)

    def Type_String(Self, String):
        """Type A String Of Characters"""

        # If Passes None or Empty String 
        if String is None:
            return False
        
        # Not Empty String
        Success = True
        for Char in String:
            # Error Indicator
            if not Self.Type_Char(Char):
                Success = False
                print("Type_String] : Invoked [Type_Char] : Failure")
        return Success

    def Press_Up(Self):
        """Press Up Arrow"""
        print("[HID] Pressing UP")
        return Self.Type_Key('UP')

    def Press_Down(Self):
        """Press Down Arrow"""
        print("[HID] Pressing DOWN")
        return Self.Type_Key('DOWN')

    def Press_Left(Self):
        """Press Left Arrow"""
        print("[HID] Pressing LEFT")
        return Self.Type_Key('LEFT')

    def Press_Right(Self):
        """Press Right Arrow"""
        print("[HID] Pressing RIGHT")
        return Self.Type_Key('RIGHT')

    def Press_Delete(Self):
        """Press Delete key (Forward Delete[Delete])"""
        print("[HID] Pressing DELETE")
        return Self.Type_Key('DELETE')

    def Press_Backspace(Self):
        """Press Backspace key"""
        print("[HID] Pressing BACKSPACE [↤]")
        return Self.Type_Key('BACKSPACE')

    def Press_Home(Self):
        """Press Home key"""
        print("[HID] Pressing HOME")
        return Self.Type_Key('HOME')

    def Press_End(Self):
        """Press End key"""
        print("[HID] Pressing END")
        return Self.Type_Key('END')

    def Press_Enter(Self):
        """Press Enter key"""
        print("[HID] Pressing ENTER")
        return Self.Type_Key('ENTER')

    def Delete_Row(Self, Method="BIOS", Time=30):
        """
        Delete Entire Row - BIOS Compatible Methods
        "BIOS": HOME : Delete Multiple Times (Safest For BIOS)
        """

        DELETE_TIME_30 = 30 
        DELETE_TIME_50 = 50 
        DELETE_TIME_80 = 80 
        
        if Time <= 30:
            Delete_Count = DELETE_TIME_30
        elif Time <= 50:
            Delete_Count = DELETE_TIME_50
        else:
            Delete_Count = DELETE_TIME_80
        
        # Print Deletion
        print(f"[Delete_Row] Deleting ROW (Method={Method}, Count={Delete_Count})")

        # BIOS-Safe Method: Go To Start, Delete Forward Many Times
        # Go to beginning of line
        Self.Type_Key('HOME')
        time.sleep(0.05)

        # Press DELETE Multiple Times (Enough To Clear A Typical Row)
        # Most BIOS are 50-80 Chars Max in Password Field
        for Iteration in range(Delete_Count):
            # DELETE Key
            if not Self.Send_Key_With_Modifier(0x4c, 0):  
                # Exit If Send Fails
                return False  
            # Small Delay Between Deletes
            time.sleep(0.02)  

        # Moved outside the loop
        return True  

    def Delete_String(Self, Text):
        """Delete String By Calculate and Pressing Corresponding Backspace For Each Character"""

        # If Passes None or Empty String 
        if Text is None:
            return False
        
        # Characters Count
        Char_Count = len(Text)
        print(f"[HID] Deleting {Char_Count} Characters (Backspace x {Char_Count})")
        Success = True

        # String Deletion 
        for Delete_Iteration in range(Char_Count):
            if not Self.Press_Backspace():
                Success = False
            # Delay between Backspaces
            time.sleep(0.03)  
        return Success

    def __del__(Self):
        """Cleanup On Destruction"""
        
        # Close HID Device - Cleanup
        Self.Close_HID_Device()


"""
+============================================================================================================+
| BluetoothHIDServer Class                                                                                   |
| Handle Bluetooth RFCOMM Protocol Listening                                                                 |
+============================================================================================================+
"""
class BluetoothHIDServer:
    
    # Bluetooth HID Server Initialization 
    def __init__(Self, Test_Mode=False):
        Self.Server_Sock = None
        Self.Client_Sock = None
        Self.Keyboard = None
        # Stacked Hardware Instance 
        Self.Hardware = Hardware()
        Self.Running = False
        Self.Port = 1
        # UUID : 8CE255C0-200A-11E0-AC64-0800200C9A66
        Self.UUID = "8CE255C0-200A-11E0-AC64-0800200C9A66"
        Self.Service_Name = "RaspberryKeyboard"
        # Test Mode
        Self.Test_Mode = Test_Mode

        # Stats Flag
        Self.Total_Connections = 0
        Self.Total_Audit_Tasks = 0

    def Initialize_Keyboard(Self):
        # Initialize HID Device
        try:
            Self.Keyboard = RaspberryKeyboard(Test_Mode=Self.Test_Mode)
            Self.Keyboard.Open_HID_Device()
            return True
        except Exception as Error:
            print(f"[Bluetooth_Server] [Initialize_Keyboard] Keyboard Init Failed: {Error}")
            return False

    def Setup_Bluetooth(Self):
        try:
            
            # Self.Server_Sock : Create a New 'bluetooth Socket' Variable - Attach an Software Python Object
            # bluetooth.BluetoothSocket() : Socket Creation
            # bluetooth.RFCOMM : Protocol Definition
            Self.Server_Sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

            # Channel Binding (Port = Channel in RFCOMM Protocol)
            # It Support 1 - 30 Protocol
            Self.Server_Sock.bind(("", Self.Port))
            # Bluetooth RFCOMM Listen to ONLY 1 Device. 
            Self.Server_Sock.listen(1)

            # Bluetooth Advertisement Service Registration
            bluetooth.advertise_service(
                Self.Server_Sock,
                Self.Service_Name,
                service_id=Self.UUID,
                service_classes=[Self.UUID, bluetooth.SERIAL_PORT_CLASS],
                profiles=[bluetooth.SERIAL_PORT_PROFILE]
                )
            return True
        
        except Exception as BluetoothSetupError:
            print(f"[ERR] Bluetooth Setup Failed: {BluetoothSetupError}")
            return False


    def Handle_Audit_Sequence(Self, Raw_Data):
        """
        [NEW STACKED LOGIC]
        Attempts to parse data as JSON. If it's a list (Action Script),
        it executes hardware signals. Otherwise, it returns False.

        Supported Commands:
        - {"Command": "HID", "Parameters": {"Key": "UP"}}
        - {"Command": "HID", "Parameters": {"Key": "DOWN"}}
        - {"Command": "HID", "Parameters": {"Key": "LEFT"}}
        - {"Command": "HID", "Parameters": {"Key": "RIGHT"}}
        - {"Command": "HID", "Parameters": {"Key": "DELETE"}}
        - {"Command": "HID", "Parameters": {"Key": "BACKSPACE"}}
        - {"Command": "HID", "Parameters": {"Key": "HOME"}}
        - {"Command": "HID", "Parameters": {"Key": "END"}}
        - {"Command": "HID", "Parameters": {"Key": "ENTER"}}
        + ==============================================================================
        - {"Command": "TYPE", "Parameters": {"Text": "hello"}}
        - {"Command": "DELETE_TEXT", "Parameters": {"Text": "hello"}}
        - {"Command": "DELETE_ROW", "Parameters": {"Method": "BIOS", "Time": 30}}
        + ==============================================================================
        - {"Command": "LED", "Parameters": {"Color": "Red", "Duration": 1.0}}
        - {"Command": "BEEP", "Parameters": {"Repeat": 2, "Pattern": "Short"}}
        - {"Command": "WAIT", "Parameters": {"Seconds": 1.0}}
        """

        try:
            # Clean up the Input Data - Remove Any BOM or Hidden Characters
            Clean_Data = Raw_Data.strip()

            # Load JSON Object Understanding into String
            Actions = json.loads(Clean_Data)

            print(f"[Handle_Audit_Sequence] Audit Challenge Received. Executing {len(Actions)} Sets of Actions.")

            if isinstance(Actions, list):
                for Action in Actions:
                    P_Command = Action.get("Command")
                    P_Parameters = Action.get("Parameters", {})

                    if P_Command == "HID":
                        # Press A Specific Key
                        Key = P_Parameters.get("Key")
                        if Key:
                            print(f"[HID] Pressing {Key}")
                            Self.Keyboard.Type_Key(Key)
                        # Blink Yellow for confirmation
                        Self.Hardware.Run("LED", {"Color": "Yellow", "Duration": 0.1})

                    elif P_Command == "TYPE":
                        # Type A String
                        Text = P_Parameters.get("Text", "")
                        print(f"[HID] Typing: {Text}")
                        Self.Keyboard.Type_String(Text)
                        Self.Hardware.Run("LED", {"Color": "Blue", "Duration": 0.1})

                    elif P_Command == "DELETE_TEXT":
                        # Delete Text By Pressing Backspace
                        Text = P_Parameters.get("Text", "")
                        Self.Keyboard.Delete_String(Text)
                        Self.Hardware.Run("LED", {"Color": "Red", "Duration": 0.1})

                    elif P_Command == "DELETE_ROW":
                        # Delete Entire Row (BIOS Compatible)
                        Method = P_Parameters.get("Method", "BIOS")
                        Time = P_Parameters.get("Time", 30)
                        Self.Keyboard.Delete_Row(Method=Method, Time=Time)
                        Self.Hardware.Run("LED", {"Color": "Red", "Duration": 0.2})

                    elif P_Command == "LED":
                        # LED Control
                        Self.Hardware.Run("LED", P_Parameters)

                    elif P_Command == "BEEP":
                        # Buzzer Control
                        Self.Hardware.Run("BEEP", P_Parameters)

                    elif P_Command == "WAIT":
                        # Wait/Sleep Control
                        Self.Hardware.Run("WAIT", P_Parameters)

                    else:
                        # Unknown Command Handler
                        print(f"[Handle_Audit_Sequence] Unknown Command: {P_Command}")

                Self.Total_Audit_Tasks += 1
                return True
                
        except json.JSONDecodeError as Error:
            # Payload is Not Valid JSON, Fallback To Normal String Mode
            if Self.Keyboard.Debug:
                print(f"[DEBUG] [Handle_Audit_Sequence] Payload Not JSON: {Error}")
            return False
        except Exception as Error:
            print(f"[Handle_Audit_Sequence] [AUDIT_ERR] : {Error}")
            return False
        return False

    def Handle_Client(Self, Client_Sock, Client_Info):
        # Log Client Connection and Increment Total Connections Counter
        print(f"[Handle_Client] CLIENT Connected: {Client_Info}")
        Self.Total_Connections += 1

        try:
            # Send Initial Handshake Message to Client Indicating Server is Ready
            Client_Sock.send("READY_FOR_AUDIT".encode('utf-8'))

            # Main Loop: Continuously Receive Data While Server is Running
            while Self.Running:
                # Receive Up To 1024 Bytes of Data From Client
                try:
                    Data = Client_Sock.recv(1024)
                except (bluetooth.btcommon.BluetoothError, ConnectionResetError, OSError):
                    # Client Disconnected Abruptly (Connection Reset By Peer)
                    print(f"[Handle_Client] Client connection reset: {Client_Info}")
                    break

                # Break Loop If Client Disconnected (Empty Data)
                # Bluetooth Disconnecting send a Disconnect (Empty Data)
                if not Data:
                    print(f"[Handle_Client] Client disconnected gracefully: {Client_Info}")
                    break

                try:
                    # Attempt To Decode Received Bytes as UTF-8 String
                    Received_Payload = Data.decode('utf-8')
                except UnicodeDecodeError:
                    # Fallback To Latin-1 Encoding For Non-UTF8 Data
                    Received_Payload = Data.decode('latin-1')

                # Ignore Empty or Whitespace-Only Payloads
                if not Received_Payload.strip():
                    continue

                # Check If Payload Is JSON Audit Command or Plain Text Password
                if Self.Handle_Audit_Sequence(Received_Payload):
                    # Audit JSON Command Executed Successfully - Send Confirmation
                    try:
                        Client_Sock.send("AUDIT_COMPLETE".encode('utf-8'))
                    except (bluetooth.btcommon.BluetoothError, ConnectionResetError, OSError):
                        print(f"[Handle_Client] Client lost during send: {Client_Info}")
                        break
                    # else Condition can be Removed as Plain Text Password is not needed anymore.
                else:
                    # Not JSON - Treat As Normal Keyboard String Input
                    # Remove Non-Printable Characters Except Newline and Tab
                    Printable_Payload = ''.join(C for C in Received_Payload if C.isprintable() or C in '\n\t')
                    if Printable_Payload:
                        # Type The Filtered String Via HID Keyboard
                        print(f"[HID] Typing Normal String: {repr(Printable_Payload)}")
                        Success = Self.Keyboard.Type_String(Printable_Payload)
                        # Set Response Based On Typing Success
                        Response = "OK" if Success else "PARTIAL_FAIL"
                    else:
                        # Payload Was All Non-Printable Characters - Ignore It
                        Response = "IGNORED"
                    # Send Response Status Back To Client
                    try:
                        Client_Sock.send(Response.encode('utf-8'))
                    except (bluetooth.btcommon.BluetoothError, ConnectionResetError, OSError):
                        print(f"[Handle_Client] Client lost during send: {Client_Info}")
                        break

        except (bluetooth.btcommon.BluetoothError, ConnectionResetError, OSError) as Error:
            # Client Connection Lost During Handshake Or Other Operation
            print(f"[Handle_Client] Client connection lost: {Client_Info} - {Error}")
        except Exception as Error:
            # Log Any Unexpected Exceptions During Client Handling
            print(f"[ERR] Unexpected client error: {Error}")
            traceback.print_exc()
        finally:
            # Always Close Client Socket When Done (Cleanup)
            try:
                Client_Sock.close()
            except Exception:
                pass
            print(f"[Handle_Client] Connection cleaned up: {Client_Info}")

    def Run(Self):
        # Initialize HID Keyboard Device - Exit If Failed
        if not Self.Initialize_Keyboard():
            print("[FATAL] Keyboard Init Failed.")
            return
        # Initialize Bluetooth RFCOMM Server - Exit If Failed
        if not Self.Setup_Bluetooth():
            print("[FATAL] Bluetooth Init Failed.")
            return

        # Log Server Startup Success and Supported Commands
        print("[RFCOMM_SERVER] : Startup Successfully")
        # Set Running Flag To True To Enable Main Loop
        Self.Running = True

        try:
            # Main Server Loop: Accept Incoming Bluetooth Connections
            while Self.Running:
                try:
                    # Block Until A Client Connects Via Bluetooth RFCOMM
                    print("[RFCOMM_SERVER] Waiting for connection...")
                    Client_Sock, Client_Info = Self.Server_Sock.accept()
                    # Handle The Connected Client (Process Commands)
                    Self.Handle_Client(Client_Sock, Client_Info)
                    # After Client Disconnects, Loop Back To Accept Next Connection
                    print(f"[RFCOMM_SERVER] Session ended. Total connections: {Self.Total_Connections}")
                except bluetooth.btcommon.BluetoothError as Error:
                    # Bluetooth Accept Error - Continue Listening
                    if Self.Running:
                        print(f"[RFCOMM_SERVER] Bluetooth error during accept: {Error}")
                        time.sleep(1)
                        continue
                except OSError as Error:
                    # OS-Level Socket Error - Continue Listening
                    if Self.Running:
                        print(f"[RFCOMM_SERVER] Socket error: {Error}")
                        time.sleep(1)
                        continue
        except KeyboardInterrupt:
            # Graceful Shutdown On Ctrl+C Interrupt
            Self.Shutdown()

    def Shutdown(Self):
        print("[SHUTDOWN] Cleaning Up...")
        
        Self.Running = False
        if Self.Keyboard:
            Self.Keyboard.Close_HID_Device()
        if Self.Server_Sock:
            Self.Server_Sock.close()
        sys.exit(0)

"""
+============================================================================================================+
| Test Sequence Logic                                                                                        |
| Handling Testing For BIOS Demonstration                                                                    |
+============================================================================================================+
| Payload                                                                                                    |
+============================================================================================================+
[
    {"Command": "LED", "Parameters": {"Color": "Red", "Duration": 1.0}},
    {"Command": "WAIT", "Parameters": {"Seconds": 1.0}},

    {"Command": "HID", "Parameters": {"Key": "UP"}},
    {"Command": "WAIT", "Parameters": {"Seconds": 0.5}},

    {"Command": "LED", "Parameters": {"Color": "Blue", "Duration": 1.0}},
    {"Command": "WAIT", "Parameters": {"Seconds": 1.0}},

    {"Command": "HID", "Parameters": {"Key": "DOWN"}},
    {"Command": "WAIT", "Parameters": {"Seconds": 0.5}},

    {"Command": "LED", "Parameters": {"Color": "Yellow", "Duration": 1.0}},
    {"Command": "WAIT", "Parameters": {"Seconds": 1.0}},

    {"Command": "HID", "Parameters": {"Key": "LEFT"}},
    {"Command": "WAIT", "Parameters": {"Seconds": 0.5}},

    {"Command": "LED_MULTI", "Parameters": {"Colors": ["Red", "Blue", "Yellow"], "Duration": 2.0}},
    {"Command": "WAIT", "Parameters": {"Seconds": 2.0}},

    {"Command": "TYPE", "Parameters": {"Text": "Assu"}},
    {"Command": "WAIT", "Parameters": {"Seconds": 2.0}},

    {"Command": "TYPE", "Parameters": {"Text": "rritz"}},
    {"Command": "WAIT", "Parameters": {"Seconds": 2.0}},

    {"Command": "DELETE_TEXT", "Parameters": {"Text": "Assurritz"}},
    {"Command": "WAIT", "Parameters": {"Seconds": 2.0}},

    {"Command": "LED", "Parameters": {"Color": "Blue", "Duration": 1.0}},
    {"Command": "WAIT", "Parameters": {"Seconds": 1.0}},

    {"Command": "HID", "Parameters": {"Key": "DOWN"}}
]
"""

def Run_Test_Sequence(Test_Mode=False):
    """
    Test Sequence:
    1. Red LED 1 Second
    2. Press UP
    3. Blue LED 1 Second
    4. Press DOWN
    5. Yellow LED 1 Second
    6. Press LEFT
    7. Red + Blue + Yellow LEDs Together 2 Seconds
    8. Type "Assu"
    9. Wait 2 Seconds
    10. Type "rritz"
    11. Wait 2 Seconds
    12. Delete "Assurritz" (9 Backspaces)
    13. Wait 2 Seconds
    14. Blue LED 1 Second
    15. Press DOWN
    """
    print("=" * 60)
    print("HID KEYBOARD TEST SEQUENCE (BIOS COMPATIBLE)")
    print("=" * 60)
    print()
    print("Test Actions:")
    print("  1. Red LED 1 Second")
    print("  2. Press UP")
    print("  3. Blue LED 1 Second")
    print("  4. Press DOWN")
    print("  5. Yellow LED 1 Second")
    print("  6. Press LEFT")
    print("  7. Red + Blue + Yellow LEDs Together 2 Seconds")
    print("  8. Type 'Assu'")
    print("  9. Wait 2 Seconds")
    print("  10. Type 'rritz'")
    print("  11. Wait 2 Seconds")
    print("  12. Delete 'Assurritz' (9 Backspaces)")
    print("  13. Wait 2 Seconds")
    print("  14. Blue LED 1 Second")
    print("  15. Press DOWN")
    print()
    print("-" * 60)

    # Log Test Mode Status
    if Test_Mode:
        print("[INFO] Running In TEST MODE (No Actual HID Output)")
    else:
        print("[INFO] Running In LIVE MODE (HID Output To /dev/hidg0)")
    print("-" * 60)
    print()

    # Initialize Keyboard Instance With Test Mode Setting
    Keyboard = RaspberryKeyboard(Test_Mode=Test_Mode)
    Keyboard.Open_HID_Device()

    # Initialize Hardware Instance For LED and Buzzer Control
    HW = Hardware()

    # Delay Before Starting Test Sequence
    print("[COUNTDOWN] Starting Test In 3 Seconds...")
    print("           (Focus On A Text Input Field!)")
    time.sleep(3)

    # ===== TEST SEQUENCE =====

    # Step 1: Red LED 1 Second
    print("\n[STEP 1/15] Red LED 1 Second")
    HW.Run("LED", {"Color": "Red", "Duration": 1.0})
    time.sleep(1.0)

    # Step 2: Press UP Arrow
    print("\n[STEP 2/15] Pressing UP Arrow")
    Keyboard.Press_Up()
    time.sleep(0.5)

    # Step 3: Blue LED 1 Second
    print("\n[STEP 3/15] Blue LED 1 Second")
    HW.Run("LED", {"Color": "Blue", "Duration": 1.0})
    time.sleep(1.0)

    # Step 4: Press DOWN Arrow
    print("\n[STEP 4/15] Pressing DOWN Arrow")
    Keyboard.Press_Down()
    time.sleep(0.5)

    # Step 5: Yellow LED 1 Second
    print("\n[STEP 5/15] Yellow LED 1 Second")
    HW.Run("LED", {"Color": "Yellow", "Duration": 1.0})
    time.sleep(1.0)

    # Step 6: Press LEFT Arrow
    print("\n[STEP 6/15] Pressing LEFT Arrow")
    Keyboard.Press_Left()
    time.sleep(0.5)

    # Step 7: Red + Blue + Yellow LEDs Together 2 Seconds
    # Direct GPIO Control To Turn On Multiple LEDs Simultaneously
    print("\n[STEP 7/15] Red + Blue + Yellow LEDs Together 2 Seconds")
    HW.LEDs["Red"].on()
    HW.LEDs["Blue"].on()
    HW.LEDs["Yellow"].on()
    time.sleep(2.0)
    HW.LEDs["Red"].off()
    HW.LEDs["Blue"].off()
    HW.LEDs["Yellow"].off()

    # Step 8: Type "Assu"
    print("\n[STEP 8/15] Typing 'Assu'")
    Keyboard.Type_String("Assu")

    # Step 9: Wait 2 Seconds
    print("\n[STEP 9/15] Wait 2 Seconds")
    time.sleep(2.0)

    # Step 10: Type "rritz"
    print("\n[STEP 10/15] Typing 'rritz'")
    Keyboard.Type_String("rritz")

    # Step 11: Wait 2 Seconds
    print("\n[STEP 11/15] Wait 2 Seconds")
    time.sleep(2.0)

    # Step 12: Delete "Assurritz" (9 Backspaces)
    print("\n[STEP 12/15] Deleting 'Assurritz' (9 Backspaces)")
    Keyboard.Delete_String("Assurritz")

    # Step 13: Wait 2 Seconds
    print("\n[STEP 13/15] Wait 2 Seconds")
    time.sleep(2.0)

    # Step 14: Blue LED 1 Second
    print("\n[STEP 14/15] Blue LED 1 Second")
    HW.Run("LED", {"Color": "Blue", "Duration": 1.0})
    time.sleep(1.0)

    # Step 15: Press DOWN Arrow
    print("\n[STEP 15/15] Pressing DOWN Arrow")
    Keyboard.Press_Down()

    # Cleanup HID Device File Descriptor
    Keyboard.Close_HID_Device()

    # Test Sequence Complete Message
    print()
    print("=" * 60)
    print("TEST SEQUENCE COMPLETE!")
    print("=" * 60)


# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================
# Usage: python3 Bluetooth_HID_Server.py [OPTIONS]
#
# Supported Modes:
# +------------------+----------------------------------------------------------+
# | Mode             | Description                                              |
# +------------------+----------------------------------------------------------+
# | --Server         | Run Bluetooth RFCOMM Server (Default Mode)               |
# |                  | - Listens For Incoming Bluetooth Connections             |
# |                  | - Accepts JSON Audit Commands Or Plain Text Passwords    |
# |                  | - Executes HID Keystrokes, LED, Buzzer, Wait Commands    |
# +------------------+----------------------------------------------------------+
# | --Test           | Run HID Hardware Test Sequence                           |
# |                  | - Tests Arrow Keys (UP/DOWN/LEFT/RIGHT) With LEDs        |
# |                  | - Tests String Typing And Deletion                       |
# |                  | - Tests Buzzer Beep Functionality                        |
# |                  | - No Bluetooth Connection Required                       |
# +------------------+----------------------------------------------------------+
# | --TestMode       | Run Server In Test Mode (No Actual HID Output)           |
# |                  | - Simulates HID Commands Without /dev/hidg0              |
# |                  | - Useful For Development And Debugging                   |
# |                  | - Prints HID Reports To Console Instead Of Sending       |
# +------------------+----------------------------------------------------------+
#
# Examples:
#   python3 Bluetooth_HID_Server.py                  # Default: Run Server Mode
#   python3 Bluetooth_HID_Server.py --Server         # Explicit: Run Server Mode
#   python3 Bluetooth_HID_Server.py --Test           # Run Hardware Test Sequence
#   python3 Bluetooth_HID_Server.py --TestMode       # Run Server Without HID Output
#   python3 Bluetooth_HID_Server.py --Test --TestMode # Run Test Without HID Output
#
# ==============================================================================

if __name__ == '__main__':
    import argparse

    # Argument Parser Initialization With Program Description
    Parser = argparse.ArgumentParser(
        description='Bluetooth HID Keyboard Server (BIOS Compatible)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 Bluetooth_HID_Server.py                  # Default: Run Server Mode
  python3 Bluetooth_HID_Server.py --Server         # Explicit: Run Server Mode
  python3 Bluetooth_HID_Server.py --Test           # Run Hardware Test Sequence
  python3 Bluetooth_HID_Server.py --TestMode       # Run Server Without HID Output
  python3 Bluetooth_HID_Server.py --Test --TestMode # Run Test Without HID Output

Supported JSON Commands:
  HID        - Press Keyboard Keys (UP, DOWN, LEFT, RIGHT, ENTER, etc.)
  TYPE       - Type A String Of Characters
  DELETE_TEXT - Delete Text By Pressing Backspace
  DELETE_ROW  - Delete Entire Row (BIOS Compatible)
  LED        - Control LEDs (Red, Yellow, Blue, White)
  BEEP       - Control Buzzer (Short, Long Pattern)
  WAIT       - Wait/Sleep For Specified Seconds
        """
    )

    # --Server : Run Bluetooth RFCOMM Server Mode
    Parser.add_argument(
        '--Server', 
        action='store_true',
        help='Run Bluetooth RFCOMM Server (Default If No Arguments Specified)'
    )

    # --Test : Run HID Hardware Test Sequence
    Parser.add_argument(
        '--Test', 
        action='store_true',
        help='Run HID Hardware Test Sequence (Arrow Keys, Typing, LEDs, Buzzer)'
    )

    # --TestMode : Enable Test Mode (No Actual HID Output To /dev/hidg0)
    Parser.add_argument(
        '--TestMode', 
        action='store_true',
        help='Enable Test Mode - Simulate HID Without Actual /dev/hidg0 Output'
    )

    # Parse Command Line Arguments
    Args = Parser.parse_args()

    # Determine If Running In Test Mode (No Actual HID Hardware)
    Test_Mode_Enabled = Args.TestMode or not os.path.exists('/dev/hidg0')

    # Log Current Mode Status
    print("=" * 60)
    print("BLUETOOTH HID KEYBOARD SERVER")
    print("=" * 60)
    if Test_Mode_Enabled:
        print("[MODE] Test Mode Enabled - No Actual HID Output")
    else:
        print("[MODE] Live Mode - HID Output To /dev/hidg0")
    print("=" * 60)

    # Execute Based On Selected Mode
    if Args.Test:
        # Run Hardware Test Sequence
        print("[ACTION] Running HID Hardware Test Sequence...")
        Run_Test_Sequence(Test_Mode=Test_Mode_Enabled)
    else:
        # Run Bluetooth RFCOMM Server (Default Mode)
        print("[ACTION] Starting Bluetooth RFCOMM Server...")
        
        # Force Bluetooth Hardware State For RPi Zero 2 W
        os.system("hciconfig hci0 up")
        os.system("hciconfig hci0 piscan")
        time.sleep(1)

        # Initialize And Run Server
        Server = BluetoothHIDServer(Test_Mode=Test_Mode_Enabled)
        Server.Run()