from typing import Any, Self

import numpy as np
from numpy.typing import NDArray

from quantem.core.datastructures.dataset2d import Dataset2d
from quantem.core.datastructures.dataset4d import Dataset4d
from quantem.core.utils.validators import ensure_valid_array


class Dataset4dstem(Dataset4d):
    """A 4D-STEM dataset class that inherits from Dataset4d.

    This class represents a 4D scanning transmission electron microscopy (STEM) dataset,
    where the data consists of a 4D array with dimensions (scan_y, scan_x, dp_y, dp_x).
    The first two dimensions represent real space scanning positions, while the latter
    two dimensions represent reciprocal space diffraction patterns.

    Attributes
    ----------
    virtual_images : dict[str, Dataset2d]
        Dictionary storing virtual images generated from the 4D-STEM dataset.
        Keys are image names and values are Dataset objects containing the images.
    """

    def __init__(
        self,
        array: NDArray | Any,
        name: str,
        origin: NDArray | tuple | list | float | int,
        sampling: NDArray | tuple | list | float | int,
        units: list[str] | tuple | list,
        signal_units: str = "arb. units",
        _token: object | None = None,
    ):
        """Initialize a 4D-STEM dataset.

        Parameters
        ----------
        array : NDArray | Any
            The underlying 4D array data
        name : str
            A descriptive name for the dataset
        origin : NDArray | tuple | list | float | int
            The origin coordinates for each dimension
        sampling : NDArray | tuple | list | float | int
            The sampling rate/spacing for each dimension
        units : list[str] | tuple | list
            Units for each dimension
        signal_units : str, optional
            Units for the array values, by default "arb. units"
        _token : object | None, optional
            Token to prevent direct instantiation, by default None
        """
        super().__init__(
            array=array,
            name=name,
            origin=origin,
            sampling=sampling,
            units=units,
            signal_units=signal_units,
            _token=_token,
        )
        self._virtual_images = {}

    @classmethod
    def from_file(cls, file_path: str, file_type: str) -> "Dataset4dstem":
        """
        Create a new Dataset4dstem from a file.

        Parameters
        ----------
        file_path : str
            Path to the data file
        file_type : str
            The type of file reader needed. See rosettasciio for supported formats
            https://hyperspy.org/rosettasciio/supported_formats/index.html

        Returns
        -------
        Dataset4dstem
            A new Dataset4dstem instance loaded from the file
        """
        # Import here to avoid circular imports
        from quantem.core.io.file_readers import read_4dstem

        return read_4dstem(file_path, file_type)

    @classmethod
    def from_array(
        cls,
        array: NDArray | Any,
        name: str | None = None,
        origin: NDArray | tuple | list | float | int | None = None,
        sampling: NDArray | tuple | list | float | int | None = None,
        units: list[str] | tuple | list | None = None,
        signal_units: str = "arb. units",
    ) -> Self:
        """
        Create a new Dataset4dstem from an array.

        Parameters
        ----------
        array : NDArray | Any
            The underlying 4D array data
        name : str | None, optional
            A descriptive name for the dataset. If None, defaults to "4D-STEM dataset"
        origin : NDArray | tuple | list | float | int | None, optional
            The origin coordinates for each dimension. If None, defaults to zeros
        sampling : NDArray | tuple | list | float | int | None, optional
            The sampling rate/spacing for each dimension. If None, defaults to ones
        units : list[str] | tuple | list | None, optional
            Units for each dimension. If None, defaults to ["pixels"] * 4
        signal_units : str, optional
            Units for the array values, by default "arb. units"

        Returns
        -------
        Dataset4dstem
            A new Dataset4dstem instance
        """
        array = ensure_valid_array(array, ndim=4)
        return cls(
            array=array,
            name=name if name is not None else "4D-STEM dataset",
            origin=origin if origin is not None else np.zeros(4),
            sampling=sampling if sampling is not None else np.ones(4),
            units=units if units is not None else ["pixels"] * 4,
            signal_units=signal_units,
            _token=cls._token,
        )

    @property
    def virtual_images(self) -> dict[str, Dataset2d]:
        """
        Dictionary storing virtual images generated from the 4D-STEM dataset.

        Returns
        -------
        dict[str, Dataset2d]
            Dictionary with image names as keys and Dataset2d objects as values
        """
        return self._virtual_images


    def get_dp(self, mode, attach:bool = True) -> Dataset2d:
    
        """
        Get mean, max, and/or median (+ more) diffraction pattern(s).

        Parameters
        ----------
        mode : list[str]
            List of diffraction pattern modes
            
        
        attach : bool, optional
            If True, attaches mean, max, and median diffraction pattern to self, by default True

        Returns
        -------
        Dataset
            datasets with specified diffraction patterns
            
        """
        
        #default to mean? 

        dp_mode = ()
        
        if 'mean' in mode:
            dp_mean = self.mean((0, 1))

            dp_mean_dataset = Dataset2d.from_array(
                array=dp_mean,
                name=self.name + "_dp_mean",
                origin=self.origin[-2:],
                sampling=self.sampling[-2:],
                units=self.units[-2:],
                signal_units=self.signal_units,
            )

            if attach is True:
                self._dp_mean = dp_mean_dataset

            dp_mode = (*dp_mode, dp_mean_dataset)

        else:
            pass

        if 'max' in mode:
            dp_max = self.max((0, 1))

            dp_max_dataset = Dataset2d.from_array(
                array=dp_max,
                name=self.name + "_dp_max",
                origin=self.origin[-2:],
                sampling=self.sampling[-2:],
                units=self.units[-2:],
                signal_units=self.signal_units,
            )

            if attach is True:
                self._dp_max = dp_max_dataset

            dp_mode = (*dp_mode, dp_max_dataset)

        else:
            pass

        if 'median' in mode:
            dp_median = np.median(self.array, axis=(0, 1))

            dp_median_dataset = Dataset2d.from_array(
                array=dp_median,
                name=self.name + "_dp_median",
                origin=self.origin[-2:],
                sampling=self.sampling[-2:],
                units=self.units[-2:],
                signal_units=self.signal_units,
            )
        
            if attach is True:
                self._dp_median = dp_median_dataset

            dp_mode = (*dp_mode, dp_median_dataset)
        
        else:
            pass

        return dp_mode
    

    @property
    def dp_mean(self) -> Dataset2d:
        """
        Dataset containing the mean diffraction pattern.

        Returns
        -------
        Dataset
            A Dataset containing the mean diffraction pattern
        """
        if hasattr(self, "_dp_mean"):
            return self._dp_mean
        else:
            print("Calculating dp_mean, attach with Dataset4dstem.get_dp_mode(mode = 'mean')")
            return self.get_dp(mode = 'mean', attach=False)


    @property
    def dp_max(self) -> Dataset2d:
        """
        Dataset containing the max diffraction pattern.

        Returns
        -------
        Dataset
            A Dataset containing the max diffraction pattern
        """
        if hasattr(self, "_dp_max"):
            return self._dp_max
        else:
            print("Calculating dp_max, attach with Dataset4dstem.get_dp_mode(mode = 'max')")
            return self.get_dp(mode = 'max', attach=False)


    @property
    def dp_median(self) -> Dataset2d:
        """
        Dataset containing the median diffraction pattern.

        Returns
        -------
        Dataset
            A Dataset containing the median diffraction pattern
        """
        if hasattr(self, "_dp_median"):
            return self._dp_median
        else:
            print("Calculating dp_median, attach with Dataset4dstem.get_dp_mode(mode = 'median')")
            return self.get_dp(mode = 'median', attach=False)
        

    def get_virtual_image(
        self,
        mask: np.ndarray,
        name: str = "virtual_image",
        attach: bool = True,
    ) -> Dataset2d:
        """
        Get virtual image.

        Parameters
        ----------
        mask : np.ndarray
            Mask for forming virtual images from 4D-STEM data. The mask should be the same
            shape as the datacube Kx and Ky
        name : str, optional
            Name of virtual image, by default "virtual_image"
        attach : bool, optional
            If True, attaches virtual image to dataset, by default True

        Returns
        -------
        Dataset
            A new Dataset with the virtual image
        """
        virtual_image = np.sum(self.array * mask, axis=(-1, -2))

        virtual_image_dataset = Dataset2d.from_array(
            array=virtual_image,
            name=name,
            origin=self.origin[0:2],
            sampling=self.sampling[0:2],
            units=self.units[0:2],
            signal_units=self.signal_units,
        )

        if attach is True:
            self._virtual_images[name] = virtual_image_dataset

        return virtual_image_dataset

    # def caitlyn_set(
    #     self,
    #     num_turns,
    #     num_points,
    #     start_radius,
    #     end_radius,
    # ):
    #     print('woagh')

    #     import matplotlib.pyplot as plt
    #     import numpy as np

    #     theta = np.linspace(0, num_turns * 2 * np.pi, num_points)
    #     r = np.linspace(start_radius, end_radius, num_points)

    #     x = r * np.cos(theta)
    #     y = r * np.sin(theta)
    #     plt.plot(x, y)
    #     plt.show()
        
        


            

    # def show(
    #     self,
    #     index : tuple[int,int] = (0,0),
    #     scalebar: ScalebarConfig | bool = True,
    #     title: str | None = None,
    #     **kwargs,
    # ):
    #     """
    #     Display the dataset and associated diffraction patterns.

    #     Parameters
    #     ----------
    #     index : tuple, optional
    #         Index for the dataset view, by default (0, 0)
    #     scalebar : ScalebarConfig | bool, optional
    #         Scalebar configuration, by default True
    #     title : str | None, optional
    #         Title for the plot, by default None
    #     **kwargs : dict
    #         Additional keyword arguments for the plot
    #     """
    #     list_of_objs = [self[index]]
    #     if hasattr(self, "_dp_mean"):
    #         list_of_objs.append(self.dp_mean)
    #     if hasattr(self, "_dp_max"):
    #         list_of_objs.append(self.dp_max)
    #     if hasattr(self, "_dp_median"):
    #         list_of_objs.append(self.dp_median)

    #     ncols = len(list_of_objs)

    #     if figax is None:
    #         figsize = (axsize[0] * ncols, axsize[1])
    #         fig, axs = plt.subplots(1, ncols, figsize=figsize, squeeze=False)
    #     else:
    #         fig, axs = figax
    #         if not isinstance(axs, np.ndarray):
    #             axs = np.array([[axs]])
    #         elif axs.ndim == 1:
    #             axs = axs.reshape(1, -1)
    #         if axs.shape != (1, ncols):
    #             raise ValueError()

    #     for obj, ax in zip(list_of_objs, axs[0]):
    #         obj.show(scalebar=scalebar, title=title, figax=(fig, ax), **kwargs)

    #     return fig, axs
