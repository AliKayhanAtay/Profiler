import time
import keyboard
from pynput.keyboard import Controller

def rapid_key_press():
    kb_controller = Controller()
    running = False  # Start in paused state
    print("Starting in 5 seconds... Switch to your target window!")
    time.sleep(5)
    
    print("\nControls:")
    print("- Press 'P' to pause/unpause")
    print("- Press 'R' to restart (if paused)")
    print("- Press 'Q' to quit")
    
    def toggle_running():
        nonlocal running
        running = not running
        print("Running" if running else "Paused")

    def restart():
        nonlocal running
        if not running:
            running = True
            print("Restarted")
    
    # Bind keys to functions
    keyboard.on_press_key('p', lambda _: toggle_running())
    keyboard.on_press_key('ü', lambda _: restart())
    f1,f2 = 'd', 'c'
    try:
        while True:
            if running:
                # Press and release X
                kb_controller.press(f1)
                time.sleep(0.01)
                kb_controller.release(f1)
                
                # Press and release S
                kb_controller.press(f2)
                time.sleep(0.01)
                kb_controller.release(f2)
                
                # Small delay between cycles
                time.sleep(0.01)
            
            # Check for quit condition
            if keyboard.is_pressed('i'):
                print("Quitting...")
                pass
                
            # Small delay to prevent high CPU usage
            time.sleep(0.001)
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        keyboard.unhook_all()  # Clean up key bindings

if __name__ == "__main__":
    rapid_key_press()