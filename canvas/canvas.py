#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Module containing a class which simplify the creation of widgets used for
drawing purposes.
"""

import cairo
import gobject
import gtk


class Canvas(gobject.GObject):
    """Window containing a drawing area for drawings.
    """

    __gsignals__ = {
            'delete-event': (gobject.SIGNAL_RUN_FIRST, None, ()),
    }
    def __init__(self, do_configure=None, do_draw=None):
        """Constructor.

        Initialize the window and pack a drawing area.

        Keywords:
            do_configure: user callback for the configure event.
            do_draw: user callback for drawing operations.
        """
        super(Canvas, self).__init__()

        window = gtk.Window()
        self.darea = gtk.DrawingArea()
        self.surface = self.context = None
        if do_configure is not None:
            self.do_configure = do_configure
        if do_draw is not None:
            self.do_draw = do_draw

        window.connect('delete-event', self.delete_cb)
        self.darea.connect('configure-event', self.configure_cb)
        self.darea.connect('expose-event', self.expose_cb)
        
        window.add(self.darea)
        window.show_all()

    def delete_cb(self, window, event):
        """Propagate the 'delete-event' signal to the user control.
        """
        self.emit('delete-event')

    def configure_cb(self, darea, event):
        """Create a private surface and its cairo context.

        Is it possible to extend the class and define a do_configure method
        invoked before the end of this.
        """
        width, height = darea.window.get_size()

        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                          width,
                                          height)
        self.context = cairo.Context(self.surface)

        try:
            self.do_configure(self, darea, event)
        except AttributeError:
            pass

        return True

    def expose_cb(self, darea, event):
        """Redraw either the whole window or a part of it.
        """
        context = darea.window.cairo_create()
        
        context.rectangle(event.area.x, event.area.y,
                          event.area.width, event.area.height)
        context.clip()
        context.set_source_surface(self.surface, 0, 0)
        context.paint()

        return False

    def refresh(self):
        """Redraw on the private context and force a refresh of the window.
        """
        try:
            self.do_draw(self)
            self.darea.queue_draw()
        except AttributeError:
            pass

        return True
