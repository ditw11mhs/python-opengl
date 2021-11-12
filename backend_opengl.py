import numpy as np
import streamlit as st
import streamlit.components.v1 as components
from streamlit.logger import update_formatter


class SimulationUtils:
    def s(self, x):
        return np.sin(x)

    def c(self, x):
        return np.cos(x)

    def cs(self, a, b):
        return self.c(a) * self.s(b)

    def sc(self, a, b):
        return self.s(a) * self.c(b)

    def ss(self, a, b):
        return self.s(a) * self.s(b)

    def cc(self, a, b):
        return self.c(a) * self.c(b)

    def info(self):
        return {
            "Constant": {
                "Height": self.H,
                "Mass": self.M,
                "dt": self.dt,
                "Duration": self.duration,
                "Length Upper Arm": self.l1,
                "Length Lower Arm": self.l2,
                "Length Upper Arm Proximal": self.l1_p,
                "Length Lower Arm Proximal": self.l2_p,
                "Mass Upper Arm": self.m1,
                "Mass Lower Arm": self.m2,
                "Upper Arm Inertia": self.inertia_1,
                "Lower Arm Inertia": self.inertia_2,
                "Theta 1 Torque": self.tau_theta_1,
                "Theta 2 Torque": self.tau_theta_2,
                "Phi 1 Torque": self.tau_phi_1,
                "Phi 2 Torque": self.tau_phi_2,
            },
            "Dynamic": {
                "Step": self.step,
                "Time Step": self.time_step(self.step),
                "Theta 1": self.theta_1(self.step),
                "Theta 2": self.theta_2(self.step),
                "Phi 1": self.phi_1(self.step),
                "Phi 2": self.phi_2(self.step),
                "Theta Dot 1": self.theta_1_dot(self.step),
                "Theta Dot 2": self.theta_2_dot(self.step),
                "Phi Dot 1": self.phi_1_dot(self.step),
                "Phi Dot 2": self.phi_2_dot(self.step),
                "Theta Dot Dot 1": self.theta_1_dot_dot(self.step),
                "Theta Dot Dot 2": self.theta_2_dot_dot(self.step),
                "Phi Dot Dot 1": self.phi_1_dot_dot(self.step),
                "Phi Dot Dot 2": self.phi_2_dot_dot(self.step),
            },
        }

    def get_number(self, row, step):
        return self.dynamic_array[row, step]

    def time_step(self, step):
        return self.get_number(0, step)

    def theta_1(self, step):
        return self.get_number(1, step)

    def theta_2(self, step):
        return self.get_number(2, step)

    def phi_1(self, step):
        return self.get_number(3, step)

    def phi_2(self, step):
        return self.get_number(4, step)

    def theta_1_dot(self, step):
        return self.get_number(5, step)

    def theta_2_dot(self, step):
        return self.get_number(6, step)

    def phi_1_dot(self, step):
        return self.get_number(7, step)

    def phi_2_dot(self, step):
        return self.get_number(8, step)

    def theta_1_dot_dot(self, step):
        return self.get_number(9, step)

    def theta_2_dot_dot(self, step):
        return self.get_number(10, step)

    def phi_1_dot_dot(self, step):
        return self.get_number(11, step)

    def phi_2_dot_dot(self, step):
        return self.get_number(12, step)

    def array_step(self, step):
        return self.dynamic_array[:, step]


class Simulation(SimulationUtils):
    def __init__(self, simulation_input) -> None:

        # Constant Parameter
        self.H = simulation_input["H"] / 100  # Height in meters
        self.M = simulation_input["M"]
        self.dt = simulation_input["dt"]
        self.duration = simulation_input["duration"]
        self.g = 9.81

        self.l1 = 0.186 * self.H
        self.l2 = 0.146 * self.H
        self.l1_p = 0.436 * self.l1
        self.l2_p = 0.430 * self.l2
        self.m1 = 0.028 * self.M
        self.m2 = 0.016 * self.M
        self.inertia_1 = self.m1 * (self.l1 * 0.322) ** 2
        self.inertia_2 = self.m2 * (self.l2 * 0.303) ** 2

        self.tau_theta_1 = simulation_input["tau_theta_1"]
        self.tau_theta_2 = simulation_input["tau_theta_2"]
        self.tau_phi_1 = simulation_input["tau_phi_1"]
        self.tau_phi_2 = simulation_input["tau_phi_2"]

        # Dynamic Parameter
        self.step = 0

        self.dynamic_array = np.zeros((13, len(np.arange(0, self.duration, self.dt))))

        self.dynamic_array[1, 0] = simulation_input["theta_1"]
        self.dynamic_array[2, 0] = simulation_input["theta_2"]
        self.dynamic_array[3, 0] = simulation_input["phi_1"]
        self.dynamic_array[4, 0] = simulation_input["phi_2"]

        self.dynamic_array[5, 0] = simulation_input["theta_1_dot"]
        self.dynamic_array[6, 0] = simulation_input["theta_2_dot"]
        self.dynamic_array[7, 0] = simulation_input["phi_1_dot"]
        self.dynamic_array[8, 0] = simulation_input["phi_2_dot"]

        self.dynamic_array[9, 0] = simulation_input["theta_1_dot_dot"]
        self.dynamic_array[10, 0] = simulation_input["theta_2_dot_dot"]
        self.dynamic_array[11, 0] = simulation_input["phi_1_dot_dot"]
        self.dynamic_array[12, 0] = simulation_input["phi_2_dot_dot"]

    def theta_1_dot_dot_function(self, plus_y, plus_y_dot):
        c = self.c
        s = self.s
        cc = self.cc
        sc = self.sc
        ss = self.ss
        cs = self.cs

        m1 = self.m1
        m2 = self.m2
        l1 = self.l1
        l1p = self.l1_p
        l2 = self.l2
        l2p = self.l2_p

        t1 = self.theta_1(self.step) + plus_y
        t2 = self.theta_2(self.step)
        p1 = self.phi_1(self.step)
        p2 = self.phi_2(self.step)
        td1 = self.theta_1_dot(self.step) + plus_y_dot
        td2 = self.theta_2_dot(self.step)
        pd1 = self.phi_1_dot(self.step)
        pd2 = self.phi_2_dot(self.step)
        tdd1 = self.theta_1_dot_dot(self.step)
        tdd2 = self.theta_2_dot_dot(self.step)
        pdd1 = self.phi_1_dot_dot(self.step)
        pdd2 = self.phi_2_dot_dot(self.step)

        upper = tdd2 * (m2 * l1 * l2p * (cc(t1, t2) * c(p1 - p2)) + ss(t1, t2))
        +td2(
            m2 * l1 * l2p * (s(t1 + t2)) * (1 - c(p1 - p2))
            + td1 * sc(t1, t2) * c(p1 - p2)
            + pd1 * cc(t1, t2) * s(p1 - p2)
            - td1 * cc(t1, t2)
        )
        +pdd2 * (m2 * l1 * l2p * cs(t1, t2) * s(p1 - p2))
        -(pd1 ** 2) * (sc(t1, t1) * (m1 * l1p ** 2 + m2 * l1 ** 2))
        +pd2 * (
            m2
            * l1
            * l2p
            * (
                cs(t1 + t2, p1 - p2)
                + td1 * ss(t1, t2) * s(p1 - p2)
                - pd1 * cs(t1, t2) * c(p1 - p2)
            )
        )
        +self.g * (m1 * l1p * s(t1) + m2 * l1 * s(t1))
        # +pdd1 * (m2 * l1 * l2p * ss(t1, t2) * c(p1 - p2))
        # +pd1 * (
        #     m2
        #     * l1
        #     * l2p
        #     * (
        #         sc(t1 + t2, p1 - p2)
        #         + pd2 * ss(t1, t2) * s(p2 - p1)
        #         - td2 * ss(t1, t2) * c(p2 - p1)
        #     )
        # )
        # +pd2(m2*l1*l2p)
        up = self.tau_theta_1 - upper
        down = m1 * l1p ** 2 + m2 * l1 ** 2 + self.inertia_1
        return up / down

    def runge_kutta_update(self, function):
        pass


class WebGL:
    pass
