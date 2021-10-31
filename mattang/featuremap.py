import random

import numpy
from pandas import DataFrame

import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib import cm
from matplotlib import colors
from mpl_toolkits.axes_grid1 import make_axes_locatable

import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature

from collections import namedtuple

from .geometry import midpoint, points_circumference, buffer_convex_hull, build_isogloss


DPI = 1200


class MattangError(Exception):
    pass


class FeatureMap:
    """Visualise linguistic data from a spreadsheet.
    """
    def __init__(self):

        self.projection = None
        self.shapefile = None
        self.extent = None
        self.discrete_markers = []
        self.continuous_markers = []
        self.colourbars = []
        self.contours = []
        
    def load_data(self, dataframe: DataFrame):
        """Precompute various things needed to plot the supplied languages and their features.
        """
        self.dataframe = dataframe
        self._plotdata = {}
        self.projection = ccrs.PlateCarree()

        for feature in self.dataframe.columns:
            data = self.dataframe[feature]
            ndata = len(data)
            try:
                if self.dataframe.dtypes[feature] in ["float64", "int64"]:
                    dtype = "continuous"
                    dnorm = colors.Normalize(min(data), max(data))
                    dgroups = self.dataframe.groupby(feature)
                    drange = int(ndata / 2)
                else:
                    dtype = "discrete"
                    dnorm = colors.BoundaryNorm([i for i in range(ndata)], ndata)
                    dgroups = self.dataframe.groupby(feature)
                    drange = len(dgroups)
                    
                self._plotdata[feature] = {"type": dtype, "norm": dnorm, "groups": dgroups, "range": drange,}
            except TypeError as error:
                # Some field types can have unhashable stuff that can't be groupby'd, so we skip them
                print("Skipping feature {} due to error \"{}\"".format(feature, error))
            
            
    def init_map(self, shapefile="", extent=None, projection=ccrs.PlateCarree()):
        """Set up map figure and axis.
        """
        self.projection = projection
        self.fig, self.axis = plt.subplots(1, 1, subplot_kw=dict(projection=projection))

        if shapefile:
            shape = ShapelyFeature(
                Reader(shapefile).geometries(),
                projection,
                edgecolor="k",
                facecolor="none",
            )
            self.axis.add_feature(shape)
            self.shapefile = shapefile
        else:
            self.axis.coastlines(resolution='50m', color='black', linewidth=1)
        if extent:
            self.axis.set_extent(extent, projection)
            self.extent = extent


    def _draw_pie_marker(self, language, features, colours, size=250):
        """sections: (feattype, proportion)
        """
        colourmaps = []
        for f, c in zip(features, colours):
            colourmaps.append(cm.get_cmap(c, self._plotdata[f]["range"]))

        cumsum = numpy.cumsum([2 for f in features])
        cumsum = cumsum / cumsum[-1]
        pie = [0] + cumsum.tolist()

        slices = []
        for r1, r2, feat, cmap in zip(pie[:-1], pie[1:], features, colourmaps):
            # Compute colour for this feature slice
            norm = self._plotdata[feat]["norm"]
            value = language[feat]
            if self._plotdata[feat]["type"] == "discrete":
                value = self._plotdata[feat]["groups"].get_group(value).index[0]
            colour = cmap(norm(value))

            # Build the pie slice
            angles = numpy.linspace(2 * numpy.pi * r1, 2 * numpy.pi * r2)
            x = [0] + numpy.cos(angles).tolist()
            y = [0] + numpy.sin(angles).tolist()
            xy = numpy.column_stack([x, y])
            marker = {"marker": xy, "facecolor": colour, "s": size, "alpha": 1,}
            slices.append(marker)

            # Save the markers for clearing the map, drawing the legend, etc.
            if self._plotdata[feat]["type"] == "discrete":
                self.discrete_markers.append(marker)
            else:
                self.continuous_markers.append(marker)

        # Draw the slices on the axis
        for slyce in slices:
            self.axis.scatter(
                [language["longitude"]],
                [language["latitude"]],
                **slyce,
                transform=self.projection,
            )


    def _draw_pie_markers(self, features, colours):
        for _, lang in self.dataframe.iterrows():
            self._draw_pie_marker(lang, features, colours)
        return


    def _draw_colourbars(self, features, colours):
        colourmaps = [cm.get_cmap(c) for c in colours]
        divider = make_axes_locatable(self.axis)

        # Need to make dummy mappables for the colourbars since we plotted the markers one by one
        for feat, cmap in zip(features, colourmaps):
            if self._plotdata[feat]["type"] == "continuous":
                mappable = cm.ScalarMappable(cmap=cmap, norm=self._plotdata[feat]["norm"])
                ax_cb = divider.new_horizontal(size="5%", pad=0.5, axes_class=plt.Axes)
                self.fig.add_axes(ax_cb)
                bar = plt.colorbar(mappable, cax=ax_cb)
                bar.set_label(feat)
                self.colourbars.append(bar)
        return


    def _draw_legend(self):
        self.axis.legend(self.discrete_markers)
        return
    

    def _draw_isogloss(self, feature, colour, style, padding):
        groupby = self._plotdata[feature]["groups"]
        group_xy = zip(
            [series.latitude for group, series in groupby],
            [series.longitude for group, series in groupby],
        )
        group_points = [list(zip(lons, lats)) for lats, lons in group_xy]
        for points in group_points:
            filtered = [p for p in points if True not in numpy.isnan(p)]
            print("points:", points, "filtered:", filtered)
            if filtered:
                isogloss = build_isogloss(filtered, padding=padding)
                for point in isogloss:
                    x, y = point
                    self.axis.plot(x, y, "".join([colour, style]), transform=self.projection)
                    
    
    def _draw_isoglosses(self, features, colour="k", style="-", padding=.1):
        for feature in features:
            self._draw_isogloss(feature, colour, style, padding)
        return

    
    def draw(self, filename, features, colours=[], isoglosses=[]):
        # Clear the map
        self.init_map(self.shapefile, self.extent, self.projection)
        
        # Check user input
        if not features:
            raise MattangError("Must specify at least one feature to plot!")
        
        for f in features:
            if f not in self.dataframe.columns:
                raise MattangError("{} is not a valid feature".format(f))

        if not colours:
            # Use randomly selected colourmaps
            allcolours = plt.colormaps()
            colours = [random.choice(allcolours) for f in features]

        if len(features) != len(colours):
            raise MattangError("Feature and colour list lengths must match")
 
        # Build and show the map
        self._draw_pie_markers(features, colours)
        if isoglosses:
            self._draw_isoglosses(isoglosses)
        #self._draw_legend()
        self._draw_colourbars(features, colours)
        self.fig.set_dpi(DPI)
        self.fig.tight_layout()
        plt.savefig(filename)
