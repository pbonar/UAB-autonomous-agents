import math
import random
import asyncio
import time
import Sensors
from collections import Counter


class DoNothing:
    """
    Does nothing
    """
    def __init__(self, a_agent):
        self.a_agent = a_agent
        self.rc_sensor = a_agent.rc_sensor
        self.i_state = a_agent.i_state

    async def run(self):
        print("Doing nothing")
        await asyncio.sleep(1)
        return True

class ForwardStop:
    """
        Moves forward till it finds an obstacle. Then stops.
    """
    STOPPED = 0
    MOVING = 1
    END = 2

    def __init__(self, a_agent):
        self.a_agent = a_agent
        self.rc_sensor = a_agent.rc_sensor
        self.i_state = a_agent.i_state
        self.state = self.STOPPED

    async def run(self):
        try:
            while True:
                if self.state == self.STOPPED:
                    # Start moving
                    await self.a_agent.send_message("action", "mf")
                    self.state = self.MOVING
                elif self.state == self.MOVING:
                    sensor_hits = self.rc_sensor.sensor_rays[Sensors.RayCastSensor.HIT]
                    if any(ray_hit == 1 for ray_hit in sensor_hits):
                        self.state = self.END
                        await self.a_agent.send_message("action", "stop")
                    else:
                        await asyncio.sleep(0)
                elif self.state == self.END:
                    break
                else:
                    print("Unknown state: " + str(self.state))
                    return False
        except asyncio.CancelledError:
            print("***** TASK Forward CANCELLED")
            await self.a_agent.send_message("action", "stop")
            self.state = self.STOPPED

class Turn:
    """
    The Drone randomly selects a degree of turn between 10 and 360,
    along with a direction (left or right), and executes the turn accordingly.
    """
    def __init__(self, a_agent):
        self.a_agent = a_agent
        self.i_state = a_agent.i_state  # Access to the agent's state

    async def run(self):
        try:
            # Get the current Y rotation
            start_rotation = self.i_state.rotation["y"]
            print(f"start rotation: {start_rotation}")

            # Randomly choose turn angle and direction
            turn_angle = random.randint(10, 360)
            direction = random.choice(["tl", "tr"])  # "tl" for left, "tr" for right"

            print(f"🔄 Turning {turn_angle} degrees to the {'left' if direction == 'tl' else 'right'}")
            
            # Calculate the target rotation
            if direction == "tl":  # Turning left (counter-clockwise)
                target_rotation = (start_rotation - turn_angle + 360) % 360
            else:  # Turning right (clockwise)
                target_rotation = (start_rotation + turn_angle) % 360

            print(f"Target rotation: {target_rotation}")

            # Send turn command
            await self.a_agent.send_message("action", direction)

            # Keep track of how much we've turned so far
            # Store initial rotation to compare against
            initial_rotation = start_rotation
            last_rotation = initial_rotation
            total_turned = 0

            # Continuously check rotation until we reach close to the target
            while True:
                current_rotation = self.i_state.rotation["y"]
                
                # Calculate how much we turned since last check
                delta = 0
                if direction == "tl":  # Left turn
                    if current_rotation > last_rotation:  # We crossed from 0 to 359
                        delta = -(last_rotation + (360 - current_rotation))
                    else:
                        delta = -(last_rotation - current_rotation)
                else:  # Right turn
                    if current_rotation < last_rotation:  # We crossed from 359 to 0
                        delta = (360 - last_rotation) + current_rotation
                    else:
                        delta = current_rotation - last_rotation
                
                # Add to total amount turned
                total_turned += delta
                print(f"Current: {current_rotation:.2f}, Delta: {delta:.2f}, Total turned: {abs(total_turned):.2f}/{turn_angle}")
                
                # Check if we've turned enough (with small tolerance)
                if abs(total_turned) >= turn_angle - 5:
                    break
                    
                # Update last rotation for next iteration
                last_rotation = current_rotation
                
                await asyncio.sleep(0.05)  # Small delay to prevent overloading

            # Stop turning
            await self.a_agent.send_message("action", "nt")

            print(f"✅ Turn complete! Started at {initial_rotation:.2f}°, ended at {current_rotation:.2f}°, turned {abs(total_turned):.2f}° towards the {'left' if direction == 'tl' else 'right'}")
            await asyncio.sleep(2)
            return True

        except asyncio.CancelledError:
            print("***** TASK Turn CANCELLED")
            await self.a_agent.send_message("action", "nt")
            return False
        except Exception as e:
            print(f"❌ Error in Turn behavior: {e}")
            await self.a_agent.send_message("action", "nt")  # Try to stop turning if there's an error
            return False


class RandomRoam:
    """
    Probability-based random movement with:
    - Forward/backward movement
    - Turns using the Turn behavior
    - Random stopping
    All based on configurable probabilities
    """
    STOPPED = 0
    MOVING_FORWARD = 1
    MOVING_BACKWARD = 2
    TURNING = 3

    def __init__(self, a_agent):
        self.a_agent = a_agent
        self.i_state = a_agent.i_state
        self.state = self.STOPPED
        self.current_turn_task = None
        
        # State transition probabilities (0-1)
        self.P_FORWARD = 0.4    # Chance to move forward
        self.P_BACKWARD = 0.2    # Chance to move backward
        self.P_TURN = 0.3        # Chance to turn (handled by Turn class)
        self.P_STOP = 0.1        # Chance to stop
        
        # Timing parameters (seconds)
        self.MIN_MOVE_TIME = 1.0
        self.MAX_MOVE_TIME = 3.0
        
        # Tracking variables
        self.state_start_time = time.time()
        self.state_duration = 0

    async def run(self):
        try:
            while True:
                current_time = time.time()
                state_age = current_time - self.state_start_time
                
                # Check if we should change state (except when turning - handled by Turn behavior)
                if self.state != self.TURNING and state_age > self.state_duration:
                    await self.choose_new_state()
                
                await asyncio.sleep(0.1)
                
        except asyncio.CancelledError:
            await self.cleanup()
            return False
        except Exception as e:
            print(f"RandomRoam error: {e}")
            await self.cleanup()
            return False

    async def choose_new_state(self):
        """Select a new random state based on probabilities"""
        rand = random.random()
        
        if rand < self.P_FORWARD:
            new_state = self.MOVING_FORWARD
        elif rand < self.P_FORWARD + self.P_BACKWARD:
            new_state = self.MOVING_BACKWARD
        elif rand < self.P_FORWARD + self.P_BACKWARD + self.P_TURN:
            new_state = self.TURNING
        else:
            new_state = self.STOPPED
        
        await self.set_state(new_state)

    async def set_state(self, new_state):
        """Clean current state and setup new state"""
        # Clean up current state
        if self.state == self.MOVING_FORWARD or self.state == self.MOVING_BACKWARD:
            await self.a_agent.send_message("action", "stop")
        elif self.state == self.TURNING and self.current_turn_task:
            self.current_turn_task.cancel()
            try:
                await self.current_turn_task
            except:
                pass
            self.current_turn_task = None
        
        # Setup new state
        if new_state == self.STOPPED:
            action = None
            self.state_duration = random.uniform(0.5, 2.0)
        elif new_state == self.MOVING_FORWARD:
            action = "mf"
            self.state_duration = random.uniform(self.MIN_MOVE_TIME, self.MAX_MOVE_TIME)
        elif new_state == self.MOVING_BACKWARD:
            action = "mb"
            self.state_duration = random.uniform(self.MIN_MOVE_TIME, self.MAX_MOVE_TIME)
        elif new_state == self.TURNING:
            # Create and run Turn behavior
            turn_behavior = Turn(self.a_agent)
            self.current_turn_task = asyncio.create_task(self.execute_turn(turn_behavior))
            # For turns, we don't set a duration - the Turn behavior will complete on its own
            self.state_duration = float('inf')
        
        if action and new_state != self.TURNING:  # Don't send action for turns - Turn behavior handles it
            await self.a_agent.send_message("action", action)
        
        self.state = new_state
        self.state_start_time = time.time()

    async def execute_turn(self, turn_behavior):
        """Execute the turn behavior and transition to new state when complete"""
        try:
            turn_success = await turn_behavior.run()
            if turn_success:
                await self.choose_new_state()  # Automatically choose next state after turn completes
        except asyncio.CancelledError:
            await turn_behavior.a_agent.send_message("action", "nt")  # Ensure turning stops
        except Exception as e:
            print(f"Error during turn execution: {e}")
        finally:
            self.current_turn_task = None

    async def cleanup(self):
        """Clean up any active movements"""
        if self.state == self.MOVING_FORWARD or self.state == self.MOVING_BACKWARD:
            await self.a_agent.send_message("action", "stop")
        elif self.state == self.TURNING and self.current_turn_task:
            self.current_turn_task.cancel()
            try:
                await self.current_turn_task
            except:
                pass
            await self.a_agent.send_message("action", "nt")

class Avoid:
    """
    Reliable obstacle avoidance with 30-degree turn increments.
    Turns until path is clear, with proper sensor checks between turns.
    """
    MOVING = 0
    TURNING = 1
    CHECKING = 2

    def __init__(self, a_agent):
        self.a_agent = a_agent
        self.rc_sensor = a_agent.rc_sensor
        self.i_state = a_agent.i_state
        self.state = self.MOVING
        
        # Configuration
        self.TURN_ANGLE = 30  # degrees per turn
        self.MIN_DISTANCE = 2  # meters
        self.REQUIRED_HITS = 1   # min sensors detecting obstacle
        
        # Turn tracking
        self.turn_start_rot = 0
        self.turn_direction = None
        self.turn_progress = 0

    async def run(self):
        try:
            print("Avoid behavior started - moving forward")
            await self.a_agent.send_message("action", "mf")
            
            while True:
                # Get fresh sensor data every iteration
                hits, distances = await self.get_sensor_data()
                obstacle_count = self.count_obstacles(hits, distances)
                
                if self.state == self.MOVING:
                    if obstacle_count >= self.REQUIRED_HITS:
                        print(f"Obstacle detected by {obstacle_count} sensors!")
                        await self.initiate_turn()
                
                elif self.state == self.TURNING:
                    if await self.update_turn():
                        self.state = self.CHECKING
                        print("Turn complete, checking path...")
                
                elif self.state == self.CHECKING:
                    hits, distances = await self.get_sensor_data()
                    obstacle_count = self.count_obstacles(hits, distances)
                    
                    if obstacle_count < self.REQUIRED_HITS:
                        print("Path clear - resuming movement")
                        await self.resume_movement()
                    else:
                        print("Path still blocked - turning more")
                        await self.continue_turn()
                
                await asyncio.sleep(0.05)
                
        except Exception as e:
            print(f"Avoid error: {e}")
            await self.cleanup()

    async def get_sensor_data(self):
        """Return fresh sensor data with debug info"""
        hits = self.rc_sensor.sensor_rays[Sensors.RayCastSensor.HIT]
        distances = self.rc_sensor.sensor_rays[Sensors.RayCastSensor.DISTANCE]
        
        # Debug print sensor data
        debug_info = [
            f"Sensor {i}: {'HIT' if h == 1 else 'clear'} {d:.2f}m"
            for i, (h, d) in enumerate(zip(hits, distances))
        ]
        print(" | ".join(debug_info))
        
        return hits, distances

    def count_obstacles(self, hits, distances):
        """Count sensors detecting obstacles within min distance"""
        return sum(
            1 for h, d in zip(hits, distances)
            if h == 1 and d is not None and d < self.MIN_DISTANCE
        )

    async def initiate_turn(self):
        """Start a new turn sequence"""
        await self.a_agent.send_message("action", "stop")
        self.turn_direction = random.choice(["tl", "tr"])
        self.turn_start_rot = self.i_state.rotation["y"]
        self.turn_progress = 0
        
        print(f"Starting {self.turn_direction} turn from {self.turn_start_rot}°")
        await self.a_agent.send_message("action", self.turn_direction)
        self.state = self.TURNING

    async def update_turn(self):
        """Update turn progress and return True when complete"""
        current_rot = self.i_state.rotation["y"]
        
        # Calculate turn progress
        if self.turn_direction == "tl":  # Left turn
            if current_rot > self.turn_start_rot:  # Crossed 0°
                delta = (360 - current_rot) + self.turn_start_rot
            else:
                delta = self.turn_start_rot - current_rot
        else:  # Right turn
            if current_rot < self.turn_start_rot:  # Crossed 360°
                delta = (360 - self.turn_start_rot) + current_rot
            else:
                delta = current_rot - self.turn_start_rot
        
        self.turn_progress = delta
        print(f"Turn progress: {delta:.1f}°/{self.TURN_ANGLE}°")
        
        if delta >= self.TURN_ANGLE - 2:  # Small tolerance
            await self.a_agent.send_message("action", "nt")
            return True
        return False

    async def continue_turn(self):
        """Continue turning in same direction"""
        self.turn_start_rot = self.i_state.rotation["y"]
        self.turn_progress = 0
        await self.a_agent.send_message("action", self.turn_direction)
        self.state = self.TURNING
        print(f"Continuing {self.turn_direction} turn")

    async def resume_movement(self):
        """Resume forward movement"""
        self.turn_direction = None
        await self.a_agent.send_message("action", "mf")
        self.state = self.MOVING

    async def cleanup(self):
        """Stop all movements"""
        if self.state == self.TURNING:
            await self.a_agent.send_message("action", "nt")
        await self.a_agent.send_message("action", "stop")
        print("Avoid behavior stopped")