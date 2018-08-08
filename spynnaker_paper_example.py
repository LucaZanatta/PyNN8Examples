from __future__ import print_function
import spynnaker8 as sim
import pylab as plt

v_reset = -65
v_thresh = -50
rngseed = 98766987
parallel_safe = True
rng = sim.NumpyRNG(seed=rngseed, parallel_safe=parallel_safe)

sim_time = 5000
coupling_multiplier = 2.
delay_distribution = sim.RandomDistribution('uniform', [1, 14], rng=rng)

cell_params_exc = {
    'tau_m': 20.0, 'cm': 1.0, 'v_rest': -65.0, 'v_reset': -65.0,
    'v_thresh': -50.0, 'tau_syn_E': 5.0, 'tau_syn_I': 15.0,
    'tau_refrac': 0.3, 'i_offset': 0}

cell_params_inh = {
    'tau_m': 20.0, 'cm': 1.0, 'v_rest': -65.0, 'v_reset': -65.0,
    'v_thresh': -50.0, 'tau_syn_E': 5.0, 'tau_syn_I': 5.0,
    'tau_refrac': 0.3, 'i_offset': 0}

# Initialise simulator
sim.setup(timestep=1, min_delay=1, max_delay=15)

# Spike sources
poisson_spike_source = sim.Population(500, sim.SpikeSourcePoisson(
    rate=50, duration=sim_time), label='poisson_source')

# Inject a spike into the network half-way through the run
spike_source_array = sim.Population(125, sim.SpikeSourceArray,
                                    {'spike_times': [sim_time // 2]},
                                    label='spike_source')

# Neuronal populations
pop_exc = sim.Population(500, sim.IF_curr_exp(**cell_params_exc),
                         label='excitatory_pop')
pop_inh = sim.Population(125, sim.IF_curr_exp(**cell_params_inh),
                         label='inhibitory_pop')

# Initialise cell membrane potential to some sub-threshold level
pop_exc.set(v=sim.RandomDistribution('uniform',
                                     [v_reset, v_thresh],
                                     rng=rng))

# Spike input projections
spike_source_projection = sim.Projection(
    spike_source_array, pop_exc,
    sim.FixedProbabilityConnector(p_connect=.1),
    synapse_type=sim.StaticSynapse(weight=0.06, delay=delay_distribution),
    receptor_type='excitatory')

# Poisson source projections
poisson_projection_exc = sim.Projection(
    poisson_spike_source, pop_exc,
    sim.FixedProbabilityConnector(p_connect=.1),
    synapse_type=sim.StaticSynapse(weight=0.06, delay=delay_distribution),
    receptor_type='excitatory')
poisson_projection_inh = sim.Projection(
    poisson_spike_source, pop_inh,
    sim.FixedProbabilityConnector(p_connect=.1),
    synapse_type=sim.StaticSynapse(weight=0.03, delay=delay_distribution),
    receptor_type='excitatory')

# Recurrent projections
exc_exc_rec = sim.Projection(
    pop_exc, pop_exc,
    sim.FixedProbabilityConnector(p_connect=.1),
    synapse_type=sim.StaticSynapse(weight=0.03, delay=delay_distribution),
    receptor_type='excitatory')
exc_exc_one_to_one_rec = sim.Projection(
    pop_exc, pop_exc,
    sim.OneToOneConnector(),
    synapse_type=sim.StaticSynapse(weight=0.03, delay=delay_distribution),
    receptor_type='excitatory')
inh_inh_rec = sim.Projection(
    pop_inh, pop_inh,
    sim.FixedProbabilityConnector(p_connect=.1),
    synapse_type=sim.StaticSynapse(weight=0.03, delay=delay_distribution),
    receptor_type='inhibitory')

# Projections between neuronal populations
exc_to_inh = sim.Projection(
    pop_exc, pop_inh,
    sim.FixedProbabilityConnector(p_connect=.2),
    synapse_type=sim.StaticSynapse(
        weight=coupling_multiplier * 0.03, delay=delay_distribution),
    receptor_type='excitatory')
inh_to_exc = sim.Projection(
    pop_inh, pop_exc,
    sim.FixedProbabilityConnector(p_connect=.2),
    synapse_type=sim.StaticSynapse(
        weight=coupling_multiplier * 0.03, delay=delay_distribution),
    receptor_type='inhibitory')

# Specify output recording
pop_exc.record('all')
pop_inh.record('spikes')

# Run simulation
sim.run(simtime=sim_time)

# Get results data
exc_data = pop_exc.get_data('spikes')
inh_data = pop_inh.get_data('spikes')


# Exit simulation -- release and clear the machine
sim.end()
import matplotlib as mlib
from spynnaker8.utilities.neo_convertor import convert_spikes
exc_spikes = convert_spikes(exc_data)
inh_spikes = convert_spikes(inh_data)

mlib.rcParams.update({'font.size': 30,
                      'font.family': 'Times New Roman'})


def plot_spikes(exc_spikes, inh_spikes, title, simtime=sim_time):
    f, ax1 = plt.subplots(1, 1, figsize=(20, 10))
    ax1.set_xlim((0, simtime))
    ax1.scatter([i[1] for i in exc_spikes], [i[0] for i in exc_spikes], s=1,
                marker="*")

    ax1.scatter([i[1] for i in inh_spikes], [i[0] + 500 for i in inh_spikes],
                s=1, marker="*", c='r')
    ax1.set_xlabel('Time(ms)')
    ax1.set_ylabel('Neuron ID')
    ax1.set_title(title)
    plt.tight_layout()
    plt.savefig(title + ".png", dpi=800)
    plt.show()

plot_spikes(exc_spikes, inh_spikes, "Random Balanced Network")





