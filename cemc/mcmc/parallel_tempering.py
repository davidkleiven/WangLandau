from ase.units import kB
import numpy as np


class ParallelTempering(object):
    def __init__(self, mc_obj=None, Tmax=1500.0, Tmin=100.0,
                 temp_scheme_file="temp_scheme.csv"):
        from cemc.mcmc import Montecarlo
        if not isinstance(mc_obj, Montecarlo):
            raise TypeError("mc_obj has to be of type Montecarlo!")

        mc_obj.T = Tmax
        self.mc_objs = [mc_obj]
        self.natoms = len(mc_obj.atoms)
        self.active_replica = 0

        self.temperature_schedule_fname = temp_scheme_file
        self.Tmax = Tmax
        self.Tmin = Tmin
        self._init_temperature_scheme()

    def _log(self, msg):
        print(msg)

    @property
    def temperature_scheme(self):
        scheme = []
        for mc in self.mc_objs:
            scheme.append(mc.T)
        return scheme

    def _init_temperature_scheme_from_file(self):
        """Initialize temperature scheme from file."""
        try:
            data = np.loadtxt(self.temperature_schedule_fname, delimiter=',')
            data = data[:, 0].tolist()
        except IOError:
            return False

        for T in data:
            new_mc = self.mc_objs[-1].copy()
            new_mc.reset()
            new_mc.T = T
            self.mc_objs.append(new_mc)
        return True

    def _init_temperature_scheme(self, target_accept=0.2):
        """Initialize the temperature scheme."""

        if self._init_temperature_scheme_from_file():
            # Temperature scheme was initialized from file
            self._log("Temperature schedule was initialized from file {}"
                      "".format(self.temperature_schedule_fname))
            return

        lowest_T = self.Tmax
        replica_count = 1
        self._log("Initializing temperature scheme")
        self.mc_objs[0].runMC(steps=10*self.natoms, equil=False)

        acceptance_ratios = [0.0]
        while lowest_T > self.Tmin:
            current_mc_obj = self.mc_objs[-1]
            self._log("{}: Temperature: {}K".format(replica_count,
                                                    current_mc_obj.T))
            new_mc, new_accept = self._find_next_temperature(
                current_mc_obj, target_accept=target_accept)
            if new_mc is None:
                break
            lowest_T = new_mc.T
            acceptance_ratios.append(new_accept)
            self.mc_objs.append(new_mc)
            replica_count += 1
        self._log("Temperature scheme initialized...")

        # Save temperature scheme
        temps = self.temperature_scheme
        data = np.vstack((temps, acceptance_ratios)).T
        np.savetxt(self.temperature_schedule_fname, data, delimiter=",",
                   header="Temperature (K), Acceptance probabability")
        self._log("Temperature scheme saved to {}"
                  "".format(self.temperature_schedule_fname))

    def _find_next_temperature(self, current_mc_obj, target_accept=0.2):
        """Find the text temperature given a target acceptance ratio."""
        nsteps = 10 * self.natoms
        current_temp = current_mc_obj.T

        trial_temp = current_temp/2.0
        accept_prob = 1.0
        new_mc_obj = current_mc_obj.copy()
        new_mc_obj.reset()
        cur_E = current_mc_obj.get_thermodynamic()["energy"]
        found_candidate_temp = False

        while accept_prob > target_accept and trial_temp > self.Tmin:
            new_mc_obj.T = trial_temp
            new_mc_obj.runMC(steps=nsteps, equil=False)
            stat = new_mc_obj.get_thermodynamic()
            E = stat["energy"]
            accept_prob = self._accept_probability(cur_E, E,
                                                   current_temp, trial_temp)
            found_candidate_temp = (accept_prob <= target_accept)
            trial_temp /= 2.0

        if not found_candidate_temp:
            return None, 0.0

        self._log("New candidate temperature: {}K. Accept rate: {}"
                  "".format(trial_temp, accept_prob))

        # Apply bisection method to refine the trial temperature
        converged = False
        upper_limit = current_temp
        lower_limit = trial_temp
        min_dT = 1E-4
        while not converged:
            new_T = 0.5 * (upper_limit + lower_limit)
            new_mc_obj.T = new_T
            new_mc_obj.runMC(steps=nsteps, equil=False)
            new_E = new_mc_obj.get_thermodynamic()["energy"]
            new_accept = self._accept_probability(cur_E, new_E,
                                                  current_temp, new_T)
            print(new_accept)
            if new_accept > target_accept:
                # Temperatures are too close --> lower the upper limit
                upper_limit = new_T
            else:
                # Temperature are too far --> increase the lower limit
                lower_limit = new_T

            if abs(new_accept - target_accept) < 0.01:
                converged = True
            elif upper_limit - lower_limit < min_dT:
                converged = True
        return new_mc_obj, new_accept

    def _accept_probability(self, E1, E2, T1, T2):
        """Return the acceptance probability."""
        dE = E1 - E2
        b1 = 1.0 / (kB * T1)
        b2 = 1.0 / (kB * T2)
        db = b1 - b2
        return np.exp(db * dE)

    def _exchange_configuration(self, mc1, mc2):
        """Exchange the configuration between two MC states."""
        symbs1 = [atom.symbol for atom in mc1.atoms]
        symbs2 = [atom.symbol for atom in mc2.atoms]
        mc1.set_symbols(symbs2)
        mc2.set_symbols(symbs1)

    def _perform_exchange_move(self, direction="up"):
        """Peform exchange moves."""
        if direction == "up":
            moves = [(i, i+1) for i in range(0, len(self.mc_objs)-1, 2)]
        else:
            moves = [(i, i-1) for i in range(len(self.mc_objs)-1, 0, -2)]

        num_accept = 0
        for move in moves:
            E1 = self.mc_objs[move[0]].current_energy_without_vib()
            E2 = self.mc_objs[move[1]].current_energy_without_vib()
            T1 = self.mc_objs[move[0]].T
            T2 = self.mc_objs[move[1]].T
            acc_prob = self._accept_probability(E1, E2, T1, T2)
            acc = np.random.rand() < acc_prob

            if acc:
                self._exchange_configuration(self.mc_objs[move[0]],
                                                self.mc_objs[move[1]])
                num_accept += 1
        self._log("Number of accepted exchange moves: {} ({} %)"
                    "".format(num_accept,
                            float(100*num_accept)/len(moves)))

    def run(self, mc_args={}, num_exchange_cycles=10):
        """Run Parallel Tempering

        :param mc_args: Dictionary with arguments to the run method
                        of the corresponding Monte Carlo object
        :param num_exchange_cycles: How many times should replica exchange
                                    be attempted
        """
        from random import choice
        exchange_move_dir = ["up", "down"]
        for replica_ech_cycle in range(num_exchange_cycles):
            for indx in range(len(self.mc_objs)):
                self.active_replica = indx
                self.mc_objs[indx].runMC(**mc_args)
            self._perform_exchange_move(direction=choice(exchange_move_dir))
