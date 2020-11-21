import numpy as np
import torch
from torch import optim
from tqdm import trange

def trainer_fn(gabor_generator, model_neuron, epochs=20000, sigma_reg_lambda=0., fixed_std=None, save_rf_every_n_epoch=None):
    
    gabor_generator.apply_changes()
    
    optimizer = optim.Adam(gabor_generator.parameters(), lr=1e-3)
    pbar = trange(epochs, desc="Loss: {}".format(np.nan), leave=True)
    saved_rfs = []
    for epoch in pbar:
        optimizer.zero_grad()
        
        # generate gabor
        gabor = gabor_generator()
        
        if fixed_std is not None:
            gabor_std = gabor.data.std()
            gabor.data = .01 * gabor.data / gabor_std
        
        loss = -model_neuron(gabor) + sigma_reg_lambda * gabor_generator.sigma.abs()
        loss.backward()
        optimizer.step()

        pbar.set_description("Loss: {:.2f}".format(loss.item()))
        
        if save_rf_every_n_epoch is not None:
            if (epoch % save_rf_every_n_epoch) == 0:
                saved_rfs.append(gabor.cpu().data.numpy())

    gabor_generator.eval();
    return gabor_generator, saved_rfs