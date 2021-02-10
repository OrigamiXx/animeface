
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision.utils import save_image
import numpy as np

from .model import Generator, Discriminator, weights_init_normal

from ..general import AnimeFaceDataset, to_loader

def train(
    epochs,
    n_critic,
    clip_value,
    dataset,
    latent_dim,
    G,
    optimizer_G,
    D,
    optimizer_D,
    device,
    verbose_interval,
    save_interval
):
    
    for epoch in range(epochs):
        for index, image in enumerate(dataset, 1):
            g_loss = None

            image = image.to(device)

            z = torch.from_numpy(np.random.normal(0, 1, (image.size(0), latent_dim)))
            z = z.type(torch.FloatTensor).to(device)

            # generate image
            fake_image = G(z)

            # discriminator loss
            d_loss = -torch.mean(D(image)) + torch.mean(D(fake_image.detach()))

            # optimize
            optimizer_D.zero_grad()
            d_loss.backward()
            optimizer_D.step()

            # clip weights
            for param in D.parameters():
                param.data.clamp_(-clip_value, clip_value)

            if index % n_critic == 0:

                # train to fool D
                g_loss = -torch.mean(D(fake_image))

                # optimize
                optimizer_G.zero_grad()
                g_loss.backward()
                optimizer_G.step()

            batches_done = epoch * len(dataset) + index

            if batches_done % verbose_interval == 0 and not g_loss == None:
                print(
                    "[Epoch %d/%d] [Batch %d/%d] [D loss: %f] [G loss: %f]"
                    % (epoch, epochs, index, len(dataset), d_loss.item(), g_loss.item())
                )
            
            fake_image.view(fake_image.size(0), -1)
            if batches_done % save_interval == 0 or batches_done == 1:
                save_image(fake_image.data[:25], "implementations/WGAN/result/%d.png" % batches_done, nrow=5, normalize=True)

def main(parser):
    batch_size = 32
    image_size = 128
    epochs = 150
    latent_dim = 200
    lr = 5.e-5
    n_critic = 5
    clip_value = 0.01

    dataset = AnimeFaceDataset(image_size)
    dataset = to_loader(dataset, batch_size)

    G = Generator(latent_dim=latent_dim)
    D = Discriminator()

    G.apply(weights_init_normal)
    D.apply(weights_init_normal)

    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    G.to(device)
    D.to(device)

    optimizer_G = optim.RMSprop(G.parameters(), lr=lr)
    optimizer_D = optim.RMSprop(D.parameters(), lr=lr)

    train(
        epochs=epochs,
        n_critic=n_critic,
        clip_value=clip_value,
        dataset=dataset,
        latent_dim=latent_dim,
        G=G,
        optimizer_G=optimizer_G,
        D=D,
        optimizer_D=optimizer_D,
        device=device,
        verbose_interval=100,
        save_interval=500
    )