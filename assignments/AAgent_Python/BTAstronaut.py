import asyncio
import random
import py_trees
import py_trees as pt
from py_trees import common
import Goals_BT
import Sensors
import time

# ===========================
# BEHAVIOUR: Do Nothing
# ===========================
class BN_DoNothing(pt.behaviour.Behaviour):
    def __init__(self, aagent):
        """
        Initializes the DoNothing behaviour.
        """
        self.my_agent = aagent
        self.my_goal = None
        super(BN_DoNothing, self).__init__("BN_DoNothing")

    def initialise(self):
        """
        Starts the DoNothing goal as an asyncio task.
        """
        print("[BN_DoNothing] Initializing...")
        self.my_goal = asyncio.create_task(Goals_BT.DoNothing(self.my_agent).run())

    def update(self):
        """
        Updates the status of the DoNothing behaviour.
        """
        if not self.my_goal.done():
            return pt.common.Status.RUNNING
        else:
            if self.my_goal.result():
                print("[BN_DoNothing] Completed with SUCCESS")
                return pt.common.Status.SUCCESS
            else:
                print("[BN_DoNothing] Completed with FAILURE")
                return pt.common.Status.FAILURE

    def terminate(self, new_status: common.Status):
        """
        Cancels the associated task when the behaviour terminates.
        """
        print(f"[BN_DoNothing] Terminating with status: {new_status}")
        self.my_goal.cancel()


# ===========================
# BEHAVIOUR: Forward Random
# ===========================
class BN_ForwardRandom(pt.behaviour.Behaviour):
    def __init__(self, aagent):
        """
        Initializes the ForwardRandom behaviour.
        """
        self.my_goal = None
        super(BN_ForwardRandom, self).__init__("BN_ForwardRandom")
        self.my_agent = aagent

    def initialise(self):
        """
        Starts the ForwardDist goal as an asyncio task.
        """
        print("[BN_ForwardRandom] Initializing...")
        self.my_goal = asyncio.create_task(Goals_BT.ForwardDist(self.my_agent, -1, 1, 5).run())

    def update(self):
        """
        Updates the status of the ForwardRandom behaviour.
        """
        if not self.my_goal.done():
            return pt.common.Status.RUNNING
        else:
            if self.my_goal.result():
                print("[BN_ForwardRandom] Completed with SUCCESS")
                return pt.common.Status.SUCCESS
            else:
                print("[BN_ForwardRandom] Completed with FAILURE")
                return pt.common.Status.FAILURE

    def terminate(self, new_status: common.Status):
        """
        Cancels the associated task when the behaviour terminates.
        """
        print(f"[BN_ForwardRandom] Terminating with status: {new_status}")
        self.my_goal.cancel()


# ===========================
# BEHAVIOUR: Turn Random
# ===========================
class BN_TurnRandom(pt.behaviour.Behaviour):
    def __init__(self, aagent):
        """
        Initializes the TurnRandom behaviour.
        """
        self.my_goal = None
        super(BN_TurnRandom, self).__init__("BN_TurnRandom")
        self.my_agent = aagent

    def initialise(self):
        """
        Starts the Turn goal as an asyncio task.
        """
        print("[BN_TurnRandom] Initializing...")
        self.my_goal = asyncio.create_task(Goals_BT.Turn(self.my_agent).run())

    def update(self):
        """
        Updates the status of the TurnRandom behaviour.
        """
        if not self.my_goal.done():
            return pt.common.Status.RUNNING
        else:
            res = self.my_goal.result()
            if res:
                print("[BN_TurnRandom] Completed with SUCCESS")
                return pt.common.Status.SUCCESS
            else:
                print("[BN_TurnRandom] Completed with FAILURE")
                return pt.common.Status.FAILURE

    def terminate(self, new_status: common.Status):
        """
        Cancels the associated task when the behaviour terminates.
        """
        print(f"[BN_TurnRandom] Terminating with status: {new_status}")
        self.my_goal.cancel()


# ===========================
# BEHAVIOUR: Avoid Obstacles
# ===========================
class BN_Avoid(pt.behaviour.Behaviour):
    """
    Behaviour-tree node wrapping our Goals_BT.Avoid obstacle-avoider.
    """
    def __init__(self, aagent):
        super(BN_Avoid, self).__init__("BN_Avoid")
        self.my_agent = aagent
        self._task = None

    def initialise(self):
        """
        Starts the Avoid.run() coroutine.
        """
        print("[BN_Avoid] Initializing...")
        self._task = asyncio.create_task(Goals_BT.Avoid(self.my_agent).run())

    def update(self):
        """
        Updates the status of the Avoid behaviour.
        """
        if not self._task.done():
            return pt.common.Status.RUNNING
        print("[BN_Avoid] Running...")
        return pt.common.Status.SUCCESS  # Avoid never “fails”

    def terminate(self, new_status):
        """
        Cancels the associated task when the behaviour terminates.
        """
        print(f"[BN_Avoid] Terminating with status: {new_status}")
        if self._task:
            self._task.cancel()


# ===========================
# BEHAVIOUR: Detect Flower
# ===========================
class BN_DetectFlower(pt.behaviour.Behaviour):
    def __init__(self, aagent):
        """
        Initializes the DetectFlower behaviour.
        """
        self.my_goal = None
        super(BN_DetectFlower, self).__init__("BN_DetectFlower")
        self.my_agent = aagent

    def initialise(self):
        """
        No initialization needed for this behaviour.
        """
        # print("[BN_DetectFlower] Initializing...")
        pass

    def update(self):
        """
        Checks if a flower is detected.
        """
        sensor_obj_info = self.my_agent.rc_sensor.sensor_rays[Sensors.RayCastSensor.OBJECT_INFO]
        for index, value in enumerate(sensor_obj_info):
            if value:  # there is a hit with an object
                if value["tag"] == "AlienFlower":  # If it is a flower
                    print("[BN_DetectFlower] Flower detected!")
                    return pt.common.Status.SUCCESS
        # print("[BN_DetectFlower] No flower detected.")
        return pt.common.Status.FAILURE

    def terminate(self, new_status: common.Status):
        """
        No termination logic needed for this behaviour.
        """
        # print(f"[BN_DetectFlower] Terminating with status: {new_status}")
        pass

# ===========================
# BEHAVIOUR: Face Flower
# ===========================
class BN_FaceFlower(pt.behaviour.Behaviour):
    def __init__(self, aagent):
        """
        Initializes the FaceFlower behaviour.
        """
        self.my_goal = None
        super(BN_FaceFlower, self).__init__("BN_FaceFlower")
        self.my_agent = aagent

    def initialise(self):
        """
        Starts the FaceFlower goal as an asyncio task.
        """
        print("[BN_FaceFlower] Initializing...")
        self.my_goal = asyncio.create_task(Goals_BT.FaceFlower(self.my_agent).run())

    def update(self):
        """
        Updates the status of the FaceFlower behaviour.
        """
        if not self.my_goal.done():
            return pt.common.Status.RUNNING
        else:
            res = self.my_goal.result()
            if res:
                print("[BN_FaceFlower] Completed with SUCCESS")
                return pt.common.Status.SUCCESS
            else:
                print("[BN_FaceFlower] Completed with FAILURE")
                return pt.common.Status.FAILURE

    def terminate(self, new_status: common.Status):
        """
        Cancels the associated task when the behaviour terminates.
        """
        print(f"[BN_FaceFlower] Terminating with status: {new_status}")
        self.my_goal.cancel()


# ===========================
# BEHAVIOUR: Walk to Flower
# ===========================
class BN_WalkToFlower(pt.behaviour.Behaviour):
    def __init__(self, aagent):
        """
        Initializes the WalkToFlower behaviour.
        """
        self.my_goal = None
        super(BN_WalkToFlower, self).__init__("BN_WalkToFlower")
        self.my_agent = aagent

    def initialise(self):
        """
        Starts the WalkToFlower goal as an asyncio task.
        """
        # print("[BN_WalkToFlower] Initializing...")
        self.my_goal = asyncio.create_task(Goals_BT.WalkToFlower(self.my_agent).run())

    def update(self):
        """
        Updates the status of the WalkToFlower behaviour.
        """
        if not self.my_goal.done():
            return pt.common.Status.RUNNING
        else:
            res = self.my_goal.result()
            if res:
                print("[BN_WalkToFlower] Completed with SUCCESS")
                return pt.common.Status.SUCCESS
            else:
                print("[BN_WalkToFlower] Completed with FAILURE")
                return pt.common.Status.FAILURE

    def terminate(self, new_status: common.Status):
        """
        Cancels the associated task when the behaviour terminates.
        """
        print(f"[BN_WalkToFlower] Terminating with status: {new_status}")
        self.my_goal.cancel()


# ===========================
# BEHAVIOUR: Walk to Base
# ===========================
class BN_WalkToBase(pt.behaviour.Behaviour):
    def __init__(self, aagent):
        """
        Initializes the WalkToBase behaviour.
        """
        self.my_goal = None
        super(BN_WalkToBase, self).__init__("BN_WalkToBase")
        self.my_agent = aagent

    def initialise(self):
        """
        Starts the WalkToBase goal as an asyncio task.
        """
        print("[BN_WalkToBase] Initializing...")
        self.my_goal = asyncio.create_task(Goals_BT.WalkToBase(self.my_agent).run())

    def update(self):
        """
        Updates the status of the WalkToBase behaviour.
        """
        if not self.my_goal.done():
            return pt.common.Status.RUNNING
        else:
            res = self.my_goal.result()
            if res:
                print("[BN_WalkToBase] Completed with SUCCESS")
                return pt.common.Status.SUCCESS
            else:
                print("[BN_WalkToBase] Completed with FAILURE")
                return pt.common.Status.FAILURE

    def terminate(self, new_status: common.Status):
        """
        Cancels the associated task when the behaviour terminates.
        """
        print(f"[BN_WalkToBase] Terminating with status: {new_status}")
        self.my_goal.cancel()


# ===========================
# BEHAVIOUR: Inventory Full
# ===========================
class BN_InventoryFull(pt.behaviour.Behaviour):
    def __init__(self, aagent):
        """
        Initializes the InventoryFull behaviour.
        """
        self.my_goal = None
        super(BN_InventoryFull, self).__init__("BN_InventoryFull")
        self.my_agent = aagent

    def initialise(self):
        """
        No initialization needed for this behaviour.
        """
        # print("[BN_InventoryFull] Initializing...")
        pass

    def update(self):
        """
        Checks if the inventory is full.
        """
        flowers = 0
        for item in self.my_agent.i_state.myInventoryList:
            if item["name"] == "AlienFlower":
                flowers = item["amount"]
                break

        if flowers >= 2:
            # print("[BN_InventoryFull] Inventory is full.")
            return pt.common.Status.SUCCESS
        else:
            # print("[BN_InventoryFull] Inventory is not full.")
            return pt.common.Status.FAILURE

    def terminate(self, new_status: common.Status):
        """
        No termination logic needed for this behaviour.
        """
        # print(f"[BN_InventoryFull] Terminating with status: {new_status}")
        pass

# ===========================
# BEHAVIOUR: Leave Flowers
# ===========================
class BN_LeaveFlowers(pt.behaviour.Behaviour):
    def __init__(self, aagent):
        """
        Initializes the LeaveFlowers behaviour.
        """
        self.my_goal = None
        super(BN_LeaveFlowers, self).__init__("BN_LeaveFlowers")
        self.my_agent = aagent

    def initialise(self):
        """
        Starts the LeaveFlowers goal as an asyncio task.
        """
        print("[BN_LeaveFlowers] Initializing...")
        self.my_goal = asyncio.create_task(Goals_BT.LeaveFlowers(self.my_agent).run())

    def update(self):
        """
        Updates the status of the LeaveFlowers behaviour.
        """
        if not self.my_goal.done():
            return pt.common.Status.RUNNING
        else:
            res = self.my_goal.result()
            if res:
                print("[BN_LeaveFlowers] Completed with SUCCESS")
                return pt.common.Status.SUCCESS
            else:
                print("[BN_LeaveFlowers] Completed with FAILURE")
                return pt.common.Status.FAILURE

    def terminate(self, new_status: common.Status):
        """
        Cancels the associated task when the behaviour terminates.
        """
        print(f"[BN_LeaveFlowers] Terminating with status: {new_status}")
        self.my_goal.cancel()


# ===========================
# BEHAVIOUR: Detect Critter
# ===========================
class BN_DetectCritter(pt.behaviour.Behaviour):
    def __init__(self, aagent):
        """
        Initializes the DetectCritter behaviour.
        """
        self.my_goal = None
        super(BN_DetectCritter, self).__init__("BN_DetectCritter")
        self.my_agent = aagent

    def initialise(self):
        """
        No initialization needed for this behaviour.
        """
        # print("[BN_DetectCritter] Initializing...")
        pass

    def update(self):
        """
        Checks if a critter is detected.
        """
        sensor_obj_info = self.my_agent.rc_sensor.sensor_rays[Sensors.RayCastSensor.OBJECT_INFO]
        for index, value in enumerate(sensor_obj_info):
            if value:  # there is a hit with an object
                if value["tag"] == "CritterMantaRay":  # Detect critter
                    print("[BN_DetectCritter] Critter detected!")
                    return pt.common.Status.SUCCESS
        # print("[BN_DetectCritter] No critter detected.")
        return pt.common.Status.FAILURE

    def terminate(self, new_status: common.Status):
        """
        No termination logic needed for this behaviour.
        """
        # print(f"[BN_DetectCritter] Terminating with status: {new_status}")
        pass

# ===========================
# BEHAVIOUR: Evade Critter
# ===========================
class BN_EvadeCritter(pt.behaviour.Behaviour):
    def __init__(self, aagent):
        """
        Initializes the EvadeCritter behaviour.
        """
        super().__init__("BN_EvadeCritter")
        self.my_agent = aagent
        self.task = None

    def initialise(self):
        """
        Starts the EvadeCritter goal as an asyncio task.
        """
        print("[BN_EvadeCritter] Initializing...")
        self.task = asyncio.create_task(Goals_BT.EvadeCritter(self.my_agent).run())

    def update(self):
        """
        Updates the status of the EvadeCritter behaviour.
        """
        if not self.task.done():
            return pt.common.Status.RUNNING
        if self.task.result():
            print("[BN_EvadeCritter] Completed with SUCCESS")
            return pt.common.Status.SUCCESS
        else:
            print("[BN_EvadeCritter] Completed with FAILURE")
            return pt.common.Status.FAILURE

    def terminate(self, new_status):
        """
        Cancels the associated task when the behaviour terminates.
        """
        print(f"[BN_EvadeCritter] Terminating with status: {new_status}")
        if self.task and not self.task.done():
            self.task.cancel()

# ===========================
# BEHAVIOUR: Is Frozen
# ===========================
class BN_DetectFrozen(pt.behaviour.Behaviour):
    def __init__(self, aagent):
        self.my_goal = None
        # print("Initializing BN_DetectInventoryFull")
        super(BN_DetectFrozen, self).__init__("BN_DetectFrozen")
        self.my_agent = aagent
        self.i_state = aagent.i_state
    def initialise(self):
        pass
    def update(self):
        if self.i_state.isFrozen:
            return pt.common.Status.SUCCESS
        return pt.common.Status.FAILURE
    def terminate(self, new_status: common.Status):
        pass



# ===========================
# BEHAVIOUR TREE: Astronaut Alone
# ===========================
class BTAstronautAlone:
    def __init__(self, aagent):
        """
        Initializes the behaviour tree for the astronaut alone scenario.
        """
        py_trees.logging.level = py_trees.logging.Level.DEBUG
        self.aagent = aagent

        # Frozen logic (highest priority)
        frozen = pt.composites.Sequence(name="Frozen", memory=False)
        frozen.add_child(BN_DetectFrozen(aagent))  # Can add more later, like unfreeze logic

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

        # Critter Avoidance Logic (diagnostic)
        detectCritter = pt.composites.Sequence(name="DetectCritter", memory=True)
        detectCritter.add_child(BN_DetectCritter(aagent))

        # Selector node
        self.root = pt.composites.Selector(name="Selector", memory=False)
        self.root.add_children([
            frozen,        # 🔝 Highest priority: stay still if frozen
            evade,
            retreat,
            detection,
            roaming,
            detectCritter
        ])

        self.behaviour_tree = pt.trees.BehaviourTree(self.root)

    def set_invalid_state(self, node):
        """
        Sets the status of a node and its children to INVALID.
        """
        node.status = pt.common.Status.INVALID
        for child in node.children:
            self.set_invalid_state(child)

    def stop_behaviour_tree(self):
        """
        Stops the behaviour tree by setting all nodes to INVALID.
        """
        self.set_invalid_state(self.root)

    async def tick(self):
        """
        Ticks the behaviour tree.
        """
        self.behaviour_tree.tick()
        await asyncio.sleep(0)
