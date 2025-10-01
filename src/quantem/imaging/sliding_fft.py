import numpy as np
import matplotlib.pyplot as plt
from quantem.core.visualization import show_2d

"""
in __init__.py change import sliding_fft as sliding_fft to SlidingFFT when class is defined

Parameters
----------
image: data in the form of an image ... might change...?
window_shape: size of the cropped image (windows) that an fft is applied to
step_pixels: spacing between windows
crop_shape: size of cropped fft result
"""

def sliding_fft(
    image,
    window_shape,
    step_pixels=None,
    num_windows=None,
    crop_shape = None,
    plot_windows = False,
):

    # default crop size if not provided
    if crop_shape is None:
        crop_shape = window_shape

    # defining window origin coords

    # rx_max and ry_max - defines max pixel value for a possible partition of the image
    rx_max = (image.shape[0] - window_shape[0]) # to include x windows at the boundary
    ry_max = (image.shape[1] - window_shape[1]) # to include y windows at the boundary

    # rx and ry - creates an array of x/y values from 0 to rx/ry_max with a set step size
    if step_pixels is not None and num_windows is None:
        rx = np.arange(0,rx_max+1,step_pixels[0])
        ry = np.arange(0,ry_max+1,step_pixels[1])

    elif step_pixels is None and num_windows is not None:
        rx = np.round(np.linspace(0,rx_max,num_windows[0])).astype('int')
        ry = np.round(np.linspace(0,ry_max,num_windows[1])).astype('int')

    elif step_pixels is None and num_windows is None:
        raise Exception('must specify step_pixels or num_windows')
        
    elif step_pixels is not None and num_windows is not None:
        raise Exception('cannot specify both step_pixels and num_windows')    
    
    # rx0 and ry0 - the "(0,0)" of each partition, indexing = ij means starting from the top left (matrix) instead of bottom left (cartesian)
        # mimics microscopy bc scanning starts from the top left
    rx0,ry0 = np.meshgrid(rx,ry,indexing = 'ij')


    # rx1 and ry1 - the following point from rx0 and ry0    
    rx1 = rx0 + window_shape[0]
    ry1 = ry0 + window_shape[1]

    # print(rx0)
    # print(rx1)
    # print(ry0)
    # print(ry1)


    # initialize full output array (4d array of 0s)
    # floating real numbers
    stack4d = np.zeros((
        rx.size,
        ry.size,
        crop_shape[0],
        crop_shape[1],
    ))

    # cropped coordinates
    # // floor divide
    # row and column have to be defined
    x_crop = (np.arange(crop_shape[0]) + (window_shape[0] - crop_shape[0])//2).astype('int')[:,None]  
    y_crop = (np.arange(crop_shape[1]) + (window_shape[1] - crop_shape[1])//2).astype('int')[None,:]


    # calculate the fft for all partitions in image
    # fft shift for visualization (switches around the resulting fft to look more like a tem diffraction pattern)
    # f1(f2(f3(image)))
    # load indices of partition > take fft > imaginary to real by taking the absolute value > perform fftshift
    
    for x_ind in range(rx.size):
        for y_ind in range(ry.size):
            stack4d[x_ind,y_ind] = np.fft.fftshift(
                np.abs(
                    np.fft.fft2(
                        image[
                            rx0[x_ind,y_ind]:rx1[x_ind,y_ind],
                            ry0[x_ind,y_ind]:ry1[x_ind,y_ind],
                        ]
                    )
                )
            )[x_crop,y_crop]



    # print(stack4d[0,0,0,:].shape)

    # initialize cropped output array (4d array of 0s)
    # stack4d_cropped = np.zeros((
    #     rx.size,
    #     ry.size,
    #     crop_shape[0],
    #     crop_shape[1],
    # ))

    # initialize index range
    # x = int(window_shape[0]/2 - crop_shape[0]/2) # = 192
    # ind_range = list(range(x, x+128)) 




    # apply index range to full output array 
    # for x_ind in range(rx.size):
        # for y_ind in range(ry.size):

            # stack4d_cropped[x_ind,y_ind] = stack4d[x_ind,y_ind,ind_range,ind_range]

    
    # # print(stack4d_cropped)
    # print(stack4d[0,0,:,:].shape)
    # print(stack4d[0,0,:,:])
    # print(stack4d[0,0,ind_range,ind_range].shape)

    # checking the plot
    # show_2d(
    #     [
    #         [stack4d[0,0,ind_range,ind_range]]
            
    #     ]
    # )

    # plot result
    # origin on the top left... conscious of axis
    if plot_windows:
        fig,ax = show_2d(
            image,
            returnfig = True,
        )
    
        
        #plotting partitions onto image
        for x in range(rx.size):
            for y in range(ry.size):
                ax.plot(
                    [ry0[x,y],ry0[x,y],ry1[x,y],ry1[x,y],ry0[x,y]],
                    [rx0[x,y],rx1[x,y],rx1[x,y],rx0[x,y],rx0[x,y]],
                )



    return stack4d