import math
import random
import asyncio
import time
import Sensors
from collections import Counter

def calculate_distance(point_a, point_b):
    distance = math.sqrt((point_b['x'] - point_a['x']) ** 2 +
                         (point_b['y'] - point_a['y']) ** 2 +
                         (point_b['z'] - point_a['z']) ** 2)
    return distance


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

class ForwardDist:
    """
        Moves forward a certain distance specified in the parameter "dist".
        If "dist" is -1, selects a random distance between the initial
        parameters of the class "d_min" and "d_max"
    """
    STOPPED = 0
    MOVING = 1
    END = 2

    def __init__(self, a_agent, dist, d_min, d_max):
        self.a_agent = a_agent
        self.rc_sensor = a_agent.rc_sensor
        self.i_state = a_agent.i_state
        self.original_dist = dist
        self.target_dist = dist
        self.d_min = d_min
        self.d_max = d_max
        self.starting_pos = a_agent.i_state.position
        self.state = self.STOPPED

    async def run(self):
        try:
            previous_dist = 0.0  # Used to detect if we are stuck
            while True:
                if self.state == self.STOPPED:
                    # starting position before moving
                    self.starting_pos = self.a_agent.i_state.position
                    # Before start moving, calculate the distance we want to move
                    if self.original_dist < 0:
                        self.target_dist = random.randint(self.d_min, self.d_max)
                    else:
                        self.target_dist = self.original_dist
                    # Start moving
                    await self.a_agent.send_message("action", "mf")
                    self.state = self.MOVING
                    # print("TARGET DISTANCE: " + str(self.target_dist))
                elif self.state == self.MOVING:
                    # If we are moving
                    await asyncio.sleep(0.5)  # Wait for a little movement
                    current_dist = calculate_distance(self.starting_pos, self.i_state.position)
                    # print(f"Current distance: {current_dist}")
                    if current_dist >= self.target_dist:  # Check if we already have covered the required distance
                        await self.a_agent.send_message("action", "ntm")
                        self.state = self.STOPPED
                        return True
                    elif previous_dist == current_dist:  # We are not moving
                        # print(f"previous dist: {previous_dist}, current dist: {current_dist}")
                        # print("NOT MOVING")
                        await self.a_agent.send_message("action", "ntm")
                        self.state = self.STOPPED
                        return False
                    previous_dist = current_dist
                else:
                    print("Unknown state: " + str(self.state))
                    return False
        except asyncio.CancelledError:
            print("***** TASK Forward CANCELLED")
            await self.a_agent.send_message("action", "ntm")
            self.state = self.STOPPED


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
        self.MIN_DISTANCE = 2  # meters to object
        self.REQUIRED_HITS = 1   # min sensors detecting obstacle
        
        # Turn tracking
        self.turn_start_rot = 0
        self.turn_direction = None
        self.turn_progress = 0

    async def run(self):
        try:
            print("Avoid behavior started - moving forward")
            await self.a_agent.send_message("action", "mf")
            self.move_start_time = time.time()  # Start moving timer
            
            while True:
                # Get fresh sensor data every iteration
                hits, distances = await self.get_sensor_data()
                obstacle_count, direction = self.count_obstacles(hits, distances)
                
                if self.state == self.MOVING:
                    if time.time() - self.move_start_time > 3.0:
                        random_direction = random.choice(["tl", "tr"])
                        random_angle = random.randint(1, 359)  # FULL random angle between 1° and 359°
                        self.TURN_ANGLE = random_angle  # set the turn angle
                        print(f"Moving forward >3s: Random turn {random_direction} for {self.TURN_ANGLE} degrees")
                        await self.initiate_turn(random_direction)
                        continue  # skip obstacle checking this tick

                    if obstacle_count >= self.REQUIRED_HITS:
                        print(f"Obstacle detected by {obstacle_count} sensors!")
                        await self.initiate_turn(direction)
                
                elif self.state == self.TURNING:
                    if await self.update_turn(direction):
                        self.state = self.CHECKING
                        print("Turn complete, checking path...")
                
                elif self.state == self.CHECKING:
                    hits, distances = await self.get_sensor_data()
                    obstacle_count, direction = self.count_obstacles(hits, distances)
                    
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
        """
            This serves two purposes:
                - Counting sensors detecting obstacles within min distance
                - Deciding what direction it should turn
        """
        count = sum(
            1 for h, d in zip(hits, distances)
            if h == 1 and d is not None and d < self.MIN_DISTANCE
            )
        if (hits[0] != 0) or (hits[1] != 0): direction = "tr"
        else: direction = "tl"
        return count, direction

    async def initiate_turn(self, direction):
        """Start a new turn sequence"""
        await self.a_agent.send_message("action", "stop")
        self.turn_direction = direction
        self.turn_start_rot = self.i_state.rotation["y"]
        self.turn_progress = 0
        
        print(f"Starting {self.turn_direction} turn from {self.turn_start_rot}°")
        await self.a_agent.send_message("action", self.turn_direction)
        self.state = self.TURNING

    async def update_turn(self, direction):
        """Update turn progress and return True when complete"""
        current_rot = self.i_state.rotation["y"]
        
        # Calculate turn progress
        if direction == "tl":  # Left turn
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
        self.move_start_time = time.time()  # NEW: reset move timer when moving again

    async def cleanup(self):
        """Stop all movements"""
        if self.state == self.TURNING:
            await self.a_agent.send_message("action", "nt")
        await self.a_agent.send_message("action", "stop")
        print("Avoid behavior stopped")

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
        self.MIN_DISTANCE = 2  # meters to object
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
                obstacle_count, direction = self.count_obstacles(hits, distances)
                
                if self.state == self.MOVING:
                    if obstacle_count >= self.REQUIRED_HITS:
                        print(f"Obstacle detected by {obstacle_count} sensors!")
                        await self.initiate_turn(direction)
                
                elif self.state == self.TURNING:
                    if await self.update_turn(direction):
                        self.state = self.CHECKING
                        print("Turn complete, checking path...")
                
                elif self.state == self.CHECKING:
                    hits, distances = await self.get_sensor_data()
                    obstacle_count, direction = self.count_obstacles(hits, distances)
                    
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
        """
            This serves two purposes:
                - Counting sensors detecting obstacles within min distance
                - Deciding what direction it should turn
        """
        count = sum(
            1 for h, d in zip(hits, distances)
            if h == 1 and d is not None and d < self.MIN_DISTANCE
            )
        if (hits[0] != 0) or (hits[1] != 0): direction = "tr"
        else: direction = "tl"
        return count, direction

    async def initiate_turn(self, direction):
        """Start a new turn sequence"""
        await self.a_agent.send_message("action", "stop")
        self.turn_direction = direction
        self.turn_start_rot = self.i_state.rotation["y"]
        self.turn_progress = 0
        
        print(f"Starting {self.turn_direction} turn from {self.turn_start_rot}°")
        await self.a_agent.send_message("action", self.turn_direction)
        self.state = self.TURNING

    async def update_turn(self, direction):
        """Update turn progress and return True when complete"""
        current_rot = self.i_state.rotation["y"]
        
        # Calculate turn progress
        if direction == "tl":  # Left turn
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


# ----------- NEW ASSIGNMENT -----------
class DirectedTurn:
    """
    The Drone randomly selects a degree of turn between 10 and 360,
    along with a direction (left or right), and executes the turn accordingly.
    """
    def __init__(self, a_agent, direction):
        self.a_agent = a_agent
        self.i_state = a_agent.i_state  # Access to the agent's state
        self.direction = direction

    async def run(self):
        try:
            # Get the current Y rotation
            start_rotation = self.i_state.rotation["y"]
            # Randomly choose turn angle and direction
            turn_angle = 1

            print(f"🔄 Turning {turn_angle} degrees to the {'left' if self.direction == 'tl' else 'right'}")
            
            # Calculate the target rotation
            if self.direction == "tl":  # Turning left (counter-clockwise)
                target_rotation = (start_rotation - turn_angle + 360) % 360
            else:  # Turning right (clockwise)
                target_rotation = (start_rotation + turn_angle) % 360

            print(f"Target rotation: {target_rotation}")

            # Send turn command
            await self.a_agent.send_message("action", self.direction)

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
                if self.direction == "tl":  # Left turn
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

            print(f"✅ Turn complete! Started at {initial_rotation:.2f}°, ended at {current_rotation:.2f}°, turned {abs(total_turned):.2f}° towards the {'left' if self.direction == 'tl' else 'right'}")
            await asyncio.sleep(0.05)
            return True

        except asyncio.CancelledError:
            print("***** TASK Turn CANCELLED")
            await self.a_agent.send_message("action", "nt")
            return False
        except Exception as e:
            print(f"❌ Error in Turn behavior: {e}")
            await self.a_agent.send_message("action", "nt")  # Try to stop turning if there's an error
            return False
        
# PHASE 1: ASTRONAUT ALONE
class FaceFlower:
    """
    Rotates the astronaut so that it's looking towards the detected flower
    """
    def __init__(self, a_agent):
        self.a_agent = a_agent
        self.rc_sensor = a_agent.rc_sensor

    def turn_direction(self, flower_idx):
        """
        Decide turn direction based on where the flower is relative to sensor index 2 (center).
        """
        if flower_idx < 2:
            return "tl"
        elif flower_idx > 2:
            return "tr"
        else:
            return None  # Already centered

    async def run(self):
        while True:
            sensor_obj_info = self.rc_sensor.sensor_rays[Sensors.RayCastSensor.OBJECT_INFO]
            flower_idx = None

            # Find the flower's current position
            for i, obj in enumerate(sensor_obj_info):
                if obj and obj["tag"] == "AlienFlower":
                    flower_idx = i
                    break

            if flower_idx is None:
                print("No flower detected")
                return False

            if flower_idx == 2:
                print("Looking towards flower")
                return True

            direction = self.turn_direction(flower_idx)
            print(f"🔄 Turning to face flower (from sensor {flower_idx} to 2), direction: {direction}")
            await DirectedTurn(self.a_agent, direction).run()
            await asyncio.sleep(0.01)

            


class WalkToFlower:
    """
    Moves forward until the inventory has more AlienFlowers than when it started.
    """
    def __init__(self, a_agent):
        self.a_agent = a_agent
        self.i_state = a_agent.i_state

    def get_flower_count(self):
        for item in self.i_state.myInventoryList:
            if item["name"] == "AlienFlower":
                return item["amount"]
        return 0

    async def run(self):
        try:
            start_count = self.get_flower_count()
            print(f"Starting with {start_count} AlienFlowers in inventory")

            # Start moving forward
            await self.a_agent.send_message("action", "mf")
            await asyncio.sleep(0.05)

            while True:
                current_count = self.get_flower_count()
                print(f"Current AlienFlowers: {current_count}")
                
                if current_count > start_count:
                    print("✅ New flower added to inventory!")
                    await self.a_agent.send_message("action", "ntm")  # Stop moving
                    return True
                await asyncio.sleep(0.1)  # Small delay between checks

        except asyncio.CancelledError:
            print("***** TASK Approach CANCELLED")
            await self.a_agent.send_message("action", "ntm")
            return False

        except Exception as e:
            print(f"❌ Error in ApproachAndCollectFlower: {e}")
            await self.a_agent.send_message("action", "ntm")
            return False


class CollectFlower:
    """
    Collects a nearby AlienFlower.
    """
    def __init__(self, a_agent):
        self.a_agent = a_agent
    
    async def run(self):
        try:
            print("Trying to collect flower...")
            await self.a_agent.send_message("action", "collect:AlienFlower") # mirar formato
            return True
        
        except Exception as e:
            print(f"Error in CollectFlower: {e}")
            return False

        
class WalkToBase:
    """
    Properly walks to base and verifies arrival using onRoute status
    with async-friendly checking.
    """
    def __init__(self, a_agent):
        self.a_agent = a_agent

    async def run(self):
        try:
            print("Initiating base navigation...")
            await self.a_agent.send_message("action", "walk_to,Base")
            
            # Give initial movement time to start
            await asyncio.sleep(0.5)
            
            # Check every 0.5 seconds until we're no longer on route
            while self.a_agent.i_state.onRoute:
                print("Still navigating to base...")
                await asyncio.sleep(0.5)
            
            print("Confirmed arrival at base!")
            return True
            
        except Exception as e:
            print(f"Base navigation error: {e}")
            return False
        
class LeaveFlowers:
    """
    Leaves 2 AlienFlowers at the base.
    """
    def __init__(self, a_agent):
        self.a_agent = a_agent

    async def run(self):
        try:
            print("Leaving flowers at the Base...")
            await self.a_agent.send_message("action", "leave,AlienFlower,2")
            asyncio.sleep(0.5)
            return True
        
        except Exception as e:
            print(f"Error in LeaveFlowers: {e}")
            return False
        
# GOALS UNIQUE TO CRITTERS
class FaceAstronaut:
    """
    Rotates the astronaut so that it's looking towards the detected flower
    """
    def __init__(self, a_agent):
        self.a_agent = a_agent
        self.rc_sensor = a_agent.rc_sensor

    def turn_direction(self, astronaut_idx):
        """
        Decide turn direction based on where the flower is relative to sensor index 2 (center).
        """
        if astronaut_idx < 2:
            return "tl"
        elif astronaut_idx > 2:
            return "tr"
        else:
            return None  # Already centered

    async def run(self):
        while True:
            sensor_obj_info = self.rc_sensor.sensor_rays[Sensors.RayCastSensor.OBJECT_INFO]
            astronaut_idx = None

            # Find the astronaut's current position
            for i, obj in enumerate(sensor_obj_info):
                if obj and obj["tag"] == "AAgentAstronaut":
                    astronaut_idx = i
                    break

            if astronaut_idx is None:
                print("No astronaut detected")
                return False

            if astronaut_idx == 2:
                print("Looking towards astronaut")
                return True

            direction = self.turn_direction(astronaut_idx)
            print(f"🔄 Turning to face flower (from sensor {astronaut_idx} to 2), direction: {direction}")
            await DirectedTurn(self.a_agent, direction).run()
            await asyncio.sleep(0.01)


class WalkToAstronaut:
    """
    Moves forward until an astronaut has been hit. //has to be finished//
    """
    def __init__(self, a_agent):
        self.a_agent = a_agent
        self.i_state = a_agent.i_state

    def get_flower_count(self):
        for item in self.i_state.myInventoryList:
            if item["name"] == "AAgentAstronaut":
                return item["amount"]
        return 0

    async def run(self):
        try:
            start_count = self.get_flower_count()
            print(f"Starting with {start_count} AlienFlowers in inventory")

            # Start moving forward
            await self.a_agent.send_message("action", "mf")
            await asyncio.sleep(0.05)

            while True:
                current_count = self.get_flower_count()
                print(f"Current AlienFlowers: {current_count}")
                
                if current_count > start_count:
                    print("✅ New flower added to inventory!")
                    await self.a_agent.send_message("action", "ntm")  # Stop moving
                    return True
                await asyncio.sleep(0.1)  # Small delay between checks

        except asyncio.CancelledError:
            print("***** TASK Approach CANCELLED")
            await self.a_agent.send_message("action", "ntm")
            return False

        except Exception as e:
            print(f"❌ Error in ApproachAndCollectFlower: {e}")
            await self.a_agent.send_message("action", "ntm")
            return False