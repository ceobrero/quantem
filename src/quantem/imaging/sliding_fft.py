import numpy as np
import matplotlib.pyplot as plt
from quantem.core.visualization import show_2d


def sliding_fft(
    image,
    window_size,
    step_size,
    crop_size=None,
    #cropping fft... implement 128...
):
    # default crop size
    if crop_size is None:
        crop_size = window_size



    # define window origin coords
    rx_max = image.shape[0] - window_size[0]
    ry_max = image.shape[1] - window_size[1]
    rx = np.arange(0,rx_max,step_size[0])
    ry = np.arange(0,ry_max,step_size[1])
    rx0,ry0 = np.meshgrid(rx,ry,indexing = 'ij')
    rx1 = rx0 + window_size[0]
    ry1 = ry0 + window_size[1]

    # initialize output array (4d array)
    #initially real numbers
    stack4d = np.zeros((
        rx.size,
        ry.size,
        crop_size[0],
        crop_size[1],
    ))


    # calculate sliding fft
    #fft shift for visualization
    for x_ind in range(rx.size):
        for y_ind in range(ry.size):
            #crop before fftshift or after fftshift
            stack4d[x_ind,y_ind] = np.fft.fftshift(
                np.abs(
                    np.fft.fft2(
                        image[
                            rx0[x_ind,y_ind]:rx1[x_ind,y_ind],
                            ry0[x_ind,y_ind]:ry1[x_ind,y_ind],
                        ]
                    )
                )
            )

   



    # plot result
    # origin on the top left... conscious of axis
    fig,ax = show_2d(
        image,
        returnfig = True,
    )
    # ax.scatter(
    #     ry0,
    #     rx0,
    #     c = 'r',
    #     s = 40,

    # )

    for x in range(rx.size):
        for y in range(ry.size):
            ax.plot(
                [ry0[x,y],ry0[x,y],ry1[x,y],ry1[x,y],ry0[x,y]],
                [rx0[x,y],rx1[x,y],rx1[x,y],rx0[x,y],rx0[x,y]],

            )





    return stack4d