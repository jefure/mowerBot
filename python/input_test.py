import os
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy" # Removes the need to have a GUI window
pygame.init()

print("Waiting for joystick... (press CTRL+C to abort)")
while True:
    try:
        try:
            pygame.joystick.init()
            # Attempt to setup the joystick
            if pygame.joystick.get_count() < 1:
                print("No joystick found")
                pygame.joystick.quit()
                time.sleep(0.1)
            else:
                # We have a joystick, attempt to initialise it!
                joystick = pygame.joystick.Joystick(0)
                break
        except pygame.error:
            pygame.joystick.quit()
            time.sleep(0.1)
    except KeyboardInterrupt:
        # CTRL+C exit, give up
        print("User aborted")

joystick.init()
try:
   running = True
   while running:
      hadEvent = False
      events = pygame.event.get()
      for event in events:
         if event.type == pygame.JOYAXISMOTION:
            # A joystick has been moved
            hadEvent = True

         if hadEvent:
            upDown = -joystick.get_axis(1)
            leftRight = -joystick.get_axis(2)
            print("UpDown: ", upDown)
            print("LeftRight: ", leftRight)
except KeyboardInterrupt:
   print("Bye")
