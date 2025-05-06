import asyncio
import random
import py_trees
import py_trees as pt
from py_trees import common
import Goals_BT
import Sensors
import time


class BN_DoNothing(pt.behaviour.Behaviour):
    def __init__(self, aagent):
        self.my_agent = aagent
        self.my_goal = None
        # print("Initializing BN_DoNothing")
        super(BN_DoNothing, self).__init__("BN_DoNothing")

    def initialise(self):
        self.my_goal = asyncio.create_task(Goals_BT.DoNothing(self.my_agent).run())

    def update(self):
        if not self.my_goal.done():
            return pt.common.Status.RUNNING
        else:
            if self.my_goal.result():
                # print("BN_DoNothing completed with SUCCESS")
                return pt.common.Status.SUCCESS
            else:
                # print("BN_DoNothing completed with FAILURE")
                return pt.common.Status.FAILURE

    def terminate(self, new_status: common.Status):
        # Finishing the behaviour, therefore we have to stop the associated task
        self.my_goal.cancel()


class BN_ForwardRandom(pt.behaviour.Behaviour):
    def __init__(self, aagent):
        self.my_goal = None
        # print("Initializing BN_ForwardRandom")
        super(BN_ForwardRandom, self).__init__("BN_ForwardRandom")
        self.logger.debug("Initializing BN_ForwardRandom")
        self.my_agent = aagent

    def initialise(self):
        self.logger.debug("Create Goals_BT.ForwardDist task")
        self.my_goal = asyncio.create_task(Goals_BT.ForwardDist(self.my_agent, -1, 1, 5).run())

    def update(self):
        if not self.my_goal.done():
            return pt.common.Status.RUNNING
        else:
            if self.my_goal.result():
                self.logger.debug("BN_ForwardRandom completed with SUCCESS")
                # print("BN_ForwardRandom completed with SUCCESS")
                return pt.common.Status.SUCCESS
            else:
                self.logger.debug("BN_ForwardRandom completed with FAILURE")
                # print("BN_ForwardRandom completed with FAILURE")
                return pt.common.Status.FAILURE

    def terminate(self, new_status: common.Status):
        # Finishing the behaviour, therefore we have to stop the associated task
        self.logger.debug("Terminate BN_ForwardRandom")
        self.my_goal.cancel()


class BN_TurnRandom(pt.behaviour.Behaviour):
    def __init__(self, aagent):
        self.my_goal = None
        # print("Initializing BN_TurnRandom")
        super(BN_TurnRandom, self).__init__("BN_TurnRandom")
        self.my_agent = aagent

    def initialise(self):
        self.my_goal = asyncio.create_task(Goals_BT.Turn(self.my_agent).run())

    def update(self):
        if not self.my_goal.done():
            return pt.common.Status.RUNNING
        else:
            res = self.my_goal.result()
            if res:
                # print("BN_Turn completed with SUCCESS")
                return pt.common.Status.SUCCESS
            else:
                # print("BN_Turn completed with FAILURE")
                return pt.common.Status.FAILURE

    def terminate(self, new_status: common.Status):
        # Finishing the behaviour, therefore we have to stop the associated task
        self.logger.debug("Terminate BN_TurnRandom")
        self.my_goal.cancel()

# BEHAVIOUR: Agent not doing random moves
class BN_Avoid(pt.behaviour.Behaviour):
    """Behaviour‐tree node wrapping our Goals_BT.Avoid obstacle‐avoider."""
    def __init__(self, aagent):
        super(BN_Avoid, self).__init__("BN_Avoid")
        self.my_agent = aagent
        self._task = None

    def initialise(self):
        # start the Avoid.run() coroutine
        self._task = asyncio.create_task(Goals_BT.Avoid(self.my_agent).run())

    def update(self):
        if not self._task.done():
            return pt.common.Status.RUNNING
        return pt.common.Status.SUCCESS  # Avoid never “fails”
    
    def terminate(self, new_status):
        if self._task:
            self._task.cancel()

# BEHAVIOUR: Agent will return SUCCESS iff it has a flower in sight
class BN_DetectFlower(pt.behaviour.Behaviour):
    def __init__(self, aagent):
        self.my_goal = None
        # print("Initializing BN_DetectFlower")
        super(BN_DetectFlower, self).__init__("BN_DetectFlower")
        self.my_agent = aagent

    def initialise(self):
        pass

    def update(self):
        sensor_obj_info = self.my_agent.rc_sensor.sensor_rays[Sensors.RayCastSensor.OBJECT_INFO]
        for index, value in enumerate(sensor_obj_info):
            if value:  # there is a hit with an object
                if value["tag"] == "AlienFlower":  # If it is a flower
                    # print("Flower detected!")
                    # print("BN_DetectFlower completed with SUCCESS")
                    return pt.common.Status.SUCCESS
        # print("No flower...")
        # print("BN_DetectFlower completed with FAILURE")
        return pt.common.Status.FAILURE

    def terminate(self, new_status: common.Status):
        pass

# BEHAVIOUR: The agent will rotate until it's facing a flower
class BN_FaceFlower(pt.behaviour.Behaviour):
    def __init__(self, aagent):
        self.my_goal = None
        # print("Initializing BN_FaceFlower")
        super(BN_FaceFlower, self).__init__("BN_FaceFlower")
        self.my_agent = aagent

    def initialise(self):
        self.my_goal = asyncio.create_task(Goals_BT.FaceFlower(self.my_agent).run())

    def update(self):
        if not self.my_goal.done():
            # print("BN_FaceFlower completed with RUNNING")
            return pt.common.Status.RUNNING
        else:
            res = self.my_goal.result()
            if res:
                print("BN_FaceFlower completed with SUCCESS")
                return pt.common.Status.SUCCESS
            else:
                print("BN_FaceFlower completed with FAILURE")
                return pt.common.Status.FAILURE

    def terminate(self, new_status: common.Status):
        self.my_goal.cancel()    

# BEHAVIOUR: Walk towards the flower (Agent has to already be facing the right direction)
class BN_WalkToFlower(pt.behaviour.Behaviour):
    def __init__(self, aagent):
        self.my_goal = None
        # print("Initializing BN_WalkToFlower")
        super(BN_WalkToFlower, self).__init__("BN_WalkToFlower")
        self.my_agent = aagent

    def initialise(self):
        self.my_goal = asyncio.create_task(Goals_BT.WalkToFlower(self.my_agent).run())

    def update(self):
        if not self.my_goal.done():
            return pt.common.Status.RUNNING
        else:
            res = self.my_goal.result()
            if res:
                print("BN_WalkToFlower completed with SUCCESS")
                return pt.common.Status.SUCCESS
            else:
                print("BN_WalkToFlower completed with FAILURE")
                return pt.common.Status.FAILURE

    def terminate(self, new_status: common.Status):
        self.my_goal.cancel()

# BEHAVIOUR: Walk to base location
class BN_WalkToBase(pt.behaviour.Behaviour):
    def __init__(self, aagent):
        self.my_goal = None
        # print("Initializing BN_WalkToBase")
        super(BN_WalkToBase, self).__init__("BN_WalkToBase")
        self.my_agent = aagent

    def initialise(self):
        self.my_goal = asyncio.create_task(Goals_BT.WalkToBase(self.my_agent).run())

    def update(self):
        if not self.my_goal.done():
            return pt.common.Status.RUNNING
        else:
            res = self.my_goal.result()
            if res:
                print("BN_WalkToBase completed with SUCCESS")
                return pt.common.Status.SUCCESS
            else:
                print("BN_WalkToBase completed with FAILURE")
                return pt.common.Status.FAILURE

    def terminate(self, new_status: common.Status):
        self.my_goal.cancel()   

# BEHAVIOUR: Check if inventory is full so that we know when to go back to base
class BN_InventoryFull(pt.behaviour.Behaviour):
    def __init__(self, aagent):
        self.my_goal = None
        super(BN_InventoryFull, self).__init__("BN_InventoryFull")
        self.my_agent = aagent

    def initialise(self):
        pass  # Don't create a task here

    def update(self):
        # Perform a direct check without async task
        flowers = 0
        for item in self.my_agent.i_state.myInventoryList:
            if item["name"] == "AlienFlower":
                flowers = item["amount"]
                break
        
        if flowers >= 2:
            # print("BN_InventoryFull completed with SUCCESS")
            return pt.common.Status.SUCCESS
        else:
            # print("BN_InventoryFull completed with FAILURE")
            return pt.common.Status.FAILURE

    def terminate(self, new_status: common.Status):
        pass  # No task to cancel


 # BEHAVIOUR: Check if inventory is full so that we know when to go back to base
class BN_LeaveFlowers(pt.behaviour.Behaviour):
    def __init__(self, aagent):
        self.my_goal = None
        super(BN_LeaveFlowers, self).__init__("BN_LeaveFlowers")
        self.my_agent = aagent

    def initialise(self):
        self.my_goal = asyncio.create_task(Goals_BT.LeaveFlowers(self.my_agent).run())

    def update(self):
        if not self.my_goal.done():
            return pt.common.Status.RUNNING
        else:
            res = self.my_goal.result()
            if res:
                print("BN_WalkToBase completed with SUCCESS")
                return pt.common.Status.SUCCESS
            else:
                print("BN_WalkToBase completed with FAILURE")
                return pt.common.Status.FAILURE

    def terminate(self, new_status: common.Status):
        self.my_goal.cancel()   



class BN_DetectCritter(pt.behaviour.Behaviour):
    def __init__(self, aagent):
        self.my_goal = None
        super(BN_DetectCritter, self).__init__("BN_DetectCritter")
        self.my_agent = aagent

    def initialise(self):
        pass

    def update(self):
        sensor_obj_info = self.my_agent.rc_sensor.sensor_rays[Sensors.RayCastSensor.OBJECT_INFO]
        for index, value in enumerate(sensor_obj_info):
            if value:  # there is a hit with an object
                if value["tag"] == "AAgentCritterMantaRay":  # Detect critter
                    return pt.common.Status.SUCCESS
        return pt.common.Status.FAILURE

    def terminate(self, new_status: pt.common.Status):
        pass

# BN for the EvadeCritter Goal
class BN_EvadeCritter(pt.behaviour.Behaviour):
    def __init__(self, aagent):
        super().__init__("BN_EvadeCritter")
        self.my_agent = aagent
        self.task = None

    def initialise(self):
        self.task = asyncio.create_task(Goals_BT.EvadeCritter(self.my_agent).run())

    def update(self):
        if not self.task.done():
            return pt.common.Status.RUNNING
        return pt.common.Status.SUCCESS if self.task.result() else pt.common.Status.FAILURE

    def terminate(self, new_status):
        if self.task and not self.task.done():
            self.task.cancel()


class BTAstronautAlone:
    def __init__(self, aagent):
        # py_trees.logging.level = py_trees.logging.Level.DEBUG

        self.aagent = aagent

        # FINAL VERSION
        # Evade Critter logic
        evade = pt.composites.Sequence(name="EvadeCritter", memory=True)
        evade.add_children([BN_DetectCritter(aagent), BN_EvadeCritter(aagent)])

        # Back to base logic
        retreat = pt.composites.Sequence(name="GoToBase", memory=True)
        retreat.add_children([BN_InventoryFull(aagent), BN_WalkToBase(aagent), BN_LeaveFlowers(aagent)])

        # Gather flower logic
        detection = pt.composites.Sequence(name="DetectFlower", memory=True)
        detection.add_children([BN_DetectFlower(aagent), BN_FaceFlower(aagent), BN_WalkToFlower(aagent)])

        # Roaming logic
        roaming = pt.composites.Sequence(name="Roaming", memory=False)
        roaming.add_child(BN_Avoid(aagent))

        # Critter Avoidance Logic
        detectCritter = pt.composites.Sequence(name="DetectCritter", memory=True)
        # TO DO : ADD MORE Behavior nodes for agent to escape from critter (E.g. turn away, walk away etc)
        # Then add it into the children below
        detectCritter.add_children([BN_DetectCritter(aagent)])
        
        # Critter Bite Logic
        # bitten = BN_HandleBite(aagent)
        
        self.root = pt.composites.Selector(name="Selector", memory=False)
        self.root.add_children([evade, retreat, detection, roaming, detectCritter])

        self.behaviour_tree = pt.trees.BehaviourTree(self.root)

    # Function to set invalid state for a node and its children recursively
    def set_invalid_state(self, node):
        node.status = pt.common.Status.INVALID
        for child in node.children:
            self.set_invalid_state(child)

    def stop_behaviour_tree(self):
        # Setting all the nodes to invalid, we force the associated asyncio tasks to be cancelled
        self.set_invalid_state(self.root)

    async def tick(self):
        self.behaviour_tree.tick()
        await asyncio.sleep(0)