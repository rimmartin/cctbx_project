#!/usr/bin/env python
#
# datablock.py
#
#  Copyright (C) 2013 Diamond Light Source
#
#  Author: James Parkhurst
#
#  This code is distributed under the BSD license, a copy of which is
#  included in the root directory of this package.

from __future__ import division


class DataBlock(object):
  ''' High level container for blocks of sweeps and imagesets. '''

  def __init__(self, imagesets):
    ''' Instantiate from a list of imagesets. '''
    # Try to get a format class
    self._format_class = None
    self._imagesets = []

    # Load imagesets
    if imagesets is not None:
      for iset in imagesets:
        self.append(iset)

  def append(self, imageset):
    ''' Add an imageset to the block. '''
    if self._format_class is None:
      try:
        self._format_class = imageset.reader().get_format_class()
      except Exception:
        pass
    else:
      assert(self._format_class == imageset.reader().get_format_class())
    self._imagesets.append(imageset)

  def extend(self, datablock):
    ''' Add two datablocks. '''
    for iset in datablock:
      self.append(iset)

  def format_class(self):
    ''' Return the format class. '''
    return self._format_class

  def extract_stills(self):
    ''' Extract all the still imagesets '''
    return list(self.iter_stills())

  def extract_sweeps(self):
    ''' Extract all the sweeps from the block. '''
    return list(self.iter_sweeps())

  def extract_imagesets(self):
    ''' Extract all imagesets. '''
    return list(self._imagesets)

  def num_images(self):
    ''' Get the number of images. '''
    return sum([len(iset) for iset in self._imagesets])

  def __len__(self):
    ''' The number of image sets. '''
    return len(self._imagesets)

  def __eq__(self, rhs):
    ''' Check if two blocks are the same. '''
    return (self._format_class == rhs._format_class
            and self._imagesets == rhs._imagesets)

  def __ne__(self, rhs):
    ''' Check if two blocks are not equal. '''
    return not self.__eq__(rhs)

  def __iter__(self):
    ''' Iterate through the imagesets. '''
    for iset in self._imagesets:
      yield iset

  def iter_sweeps(self):
    ''' Iterate over sweep groups. '''
    from dxtbx.imageset import ImageSweep
    for iset in self._imagesets:
      if isinstance(iset, ImageSweep):
        yield iset

  def iter_stills(self):
    ''' Iterate over still groups. '''
    from dxtbx.imageset import ImageSweep
    for iset in self._imagesets:
      if not isinstance(iset, ImageSweep):
        yield iset

  def unique_beams(self):
    ''' Iterate through unique beams. '''
    from dxtbx.imageset import ImageSweep
    from collections import OrderedDict
    obj = OrderedDict()
    for iset in self._imagesets:
      if isinstance(iset, ImageSweep):
        obj[iset.get_beam()] = None
      else:
        for i in range(len(iset)):
          obj[iset.get_beam(i)] = None
    return obj.keys()

  def unique_detectors(self):
    ''' Iterate through unique detectors. '''
    from dxtbx.imageset import ImageSweep
    from collections import OrderedDict
    obj = OrderedDict()
    for iset in self._imagesets:
      if isinstance(iset, ImageSweep):
        obj[iset.get_detector()] = None
      else:
        for i in range(len(iset)):
          obj[iset.get_detector(i)] = None
    return obj.keys()

  def unique_goniometers(self):
    ''' Iterate through unique goniometers. '''
    from dxtbx.imageset import ImageSweep
    from collections import OrderedDict
    obj = OrderedDict()
    for iset in self._imagesets:
      if isinstance(iset, ImageSweep):
        obj[iset.get_goniometer()] = None
      else:
        for i in range(len(iset)):
          try:
            model = iset.get_goniometer(i)
            if model is not None:
              obj[model] = None
          except Exception:
            pass
    return obj.keys()

  def unique_scans(self):
    ''' Iterate through unique scans. '''
    from dxtbx.imageset import ImageSweep
    from collections import OrderedDict
    obj = OrderedDict()
    for iset in self._imagesets:
      if isinstance(iset, ImageSweep):
        obj[iset.get_scan()] = None
      else:
        for i in range(len(iset)):
          try:
            model = iset.get_scan(i)
            if model is not None:
              obj[model] = None
          except Exception:
            pass
    return obj.keys()

  def to_dict(self):
    ''' Convert the datablock to a dictionary '''
    from collections import OrderedDict
    from itertools import groupby
    from dxtbx.imageset import ImageSweep
    from dxtbx.format.FormatMultiImage import FormatMultiImage

    # Get a list of all the unique models
    b = list(self.unique_beams())
    d = list(self.unique_detectors())
    g = list(self.unique_goniometers())
    s = list(self.unique_scans())

    # Create the data block dictionary
    result = OrderedDict()
    result['__id__'] = 'DataBlock'
    result['imageset'] = []

    # Loop through all the imagesets
    for iset in self._imagesets:
      if isinstance(iset, ImageSweep):
        if issubclass(iset.reader().get_format_class(), FormatMultiImage):
          template = iset.reader().get_path()
        else:
          template = iset.get_template()
        result['imageset'].append(OrderedDict([
            ('__id__', 'ImageSweep'),
            ('template',   template),
            ('beam',       b.index(iset.get_beam())),
            ('detector',   d.index(iset.get_detector())),
            ('goniometer', g.index(iset.get_goniometer())),
            ('scan',       s.index(iset.get_scan()))
          ]))
      else:
        image_list = []
        for i in range(len(iset)):
          image_dict = OrderedDict()
          image_dict['filename'] = iset.get_filename(i)
          try:
            image_dict['beam'] = b.index(iset.get_beam(i))
          except Exception:
            pass
          try:
            image_dict['detector'] = d.index(iset.get_detector())
          except Exception:
            pass
          try:
            image_dict['goniometer'] = g.index(iset.get_goniometer())
          except Exception:
            pass
          try:
            image_dict['scan'] = s.index(iset.get_scan())
          except Exception:
            pass
          image_list.append(image_dict)
        result['imageset'].append(
          OrderedDict([
            ('__id__', 'ImageSet'),
            ('images', image_list)]))

    # Add the models to the dictionary
    result['beam'] = [bb.to_dict() for bb in b]
    result['detector'] = [dd.to_dict() for dd in d]
    result['goniometer'] = [gg.to_dict() for gg in g]
    result['scan'] = [ss.to_dict() for ss in s]

    # Return the data block as a dictionary
    return result


class FormatChecker(object):
  ''' A helper class to find the image format by first checking
  the last format that was used. '''

  def __init__(self):
    ''' Set the format class to none. '''
    self._format_class = None

  def check_child_formats(self, filename):
    ''' If a child format understands the file better than return that,
    otherwise return the current format. '''
    fmt = self._format_class
    for child in self._format_class._children:
      if child.understand(filename):
        fmt = child
    return fmt

  def understand(self, filename):
    ''' Check if the data block format understands the given file. This
    function checks the method resolution order for the format class and
    calls the understand methods of each parent down to the bottom level.
    Just calling the format class understand method directly can result
    in problems. This is really a workaround for a bug in the way that
    the format understand method works. Furthermore, the FormatStill
    class does not have an understand method so we have to check that
    the "understand" method is present in the class dictionary before
    we actually do the call. '''
    from dxtbx.format.Format import Format
    mro = self._format_class.mro()[::-1]
    if len(mro) <= 2 or mro[0] != object or mro[1] != Format:
      return False
    for m in mro[2:]:
      if "understand" in m.__dict__ and m.understand(filename) == False:
        return False
    return True

  def __call__(self, filename):
    ''' Check the current and child formats, otherwise search the registry. '''
    from dxtbx.format.Registry import Registry
    try:
      if self._format_class == None or not self.understand(filename):
        self._format_class = Registry.find(filename)
      self._format_class = self.check_child_formats(filename)
    except Exception:
      return None
    return self._format_class


class DataBlockFilenameImporter(object):
  ''' A class to import a datablock from image files. '''
  def __init__(self, filenames, verbose=False):
    ''' Import the datablocks from the given filenames. '''
    from itertools import groupby
    from dxtbx.format.Registry import Registry
    from dxtbx.format.FormatMultiImage import FormatMultiImage

    # Init the datablock list
    self.unhandled = []
    self.datablocks = []

    # A function to append or create a new datablock
    def append_to_datablocks(iset):
      try:
        self.datablocks[-1].append(iset)
      except Exception:
        self.datablocks.append(DataBlock([iset]))
        if verbose: print 'Starting datablock %d' % len(self.datablocks)

    # Iterate through groups of files by format class
    find_format = FormatChecker()
    for fmt, group in groupby(filenames, lambda f: find_format(f)):
      if fmt is None:
        self.unhandled.extend(group)
      elif issubclass(fmt, FormatMultiImage):
        for filename in group:
          imageset = self._create_single_file_imageset(fmt, filename)
          append_to_datablocks(imageset)
          if verbose: print 'Loaded file: %s' % filename
      else:
        records = self._extract_file_metadata(fmt, group)
        for group, items in groupby(records, lambda r: r.group):
          imageset = self._create_multi_file_imageset(fmt, list(items))
          append_to_datablocks(imageset)

  def _extract_file_metadata(self, format_class, filenames):
    ''' Extract the file meta data in order to sort them. '''
    from dxtbx.sweep_filenames import template_regex

    class Record(object):
      def __init__(self, beam=None, detector=None, goniometer=None, scan=None,
                   template=None, filename = None, index=None, group=None):
        self.beam = beam
        self.detector = detector
        self.goniometer = goniometer
        self.scan = scan
        self.template = template
        self.filename = filename
        self.index = index
        self.group = group

    # Loop through all the filenames
    records = []
    group = 0
    for filename in filenames:

      # Read the image
      fmt = format_class(filename)

      # Get the meta data from the format
      try: b = fmt.get_beam()
      except Exception: b = None
      try: d = fmt.get_detector()
      except Exception: d = None
      try: g = fmt.get_goniometer()
      except Exception: g = None
      try: s = fmt.get_scan()
      except Exception: s = None

      # Get the template and index if possible
      if s is not None and abs(s.get_oscillation()[1]) > 0.0:
        template, index = template_regex(filename)
      else:
        template, index = None, None

      # Check the last record if available
      if len(records) > 0:
        last = records[-1]
        same = [False, False, False]
        if last.beam == b:
          b = last.beam
          same[0] = True
        if last.detector == d:
          d = last.detector
          same[1] = True
        if last.goniometer == g:
          g = last.goniometer
          same[2] = True

        # If the last was not a sweep then if the current is a sweep or none of
        # the models are the same, increment. Otherwise if the current is not a
        # sweep or if both sweeps don't share all models increment. If both
        # share, models try scan and increment if exception.
        if last.template is None:
          if template is not None or not any(same):
            group += 1
        else:
          if template is None or not all(same):
            group += 1
          else:
            try:
              last.scan += s
              last.index = index
              continue
            except Exception:
              group += 1

      # Add a record
      records.append(Record(
        beam=b, detector=d, goniometer=g, scan=s,
        template=template, filename = filename,
        index=index, group=group))

    # Return the records
    return records

  def _create_multi_file_imageset(self, format_class, records):
    ''' Create a mulit file sweep or imageset. '''
    from dxtbx.imageset import MultiFileReader, ImageSetFactory

    # Make either an imageset or sweep
    if len(records) == 1 and records[0].template is not None:

      # Get the image range
      image_range = records[0].scan.get_image_range()
      image_range = (image_range[0], image_range[1]+1)

      # Create the sweep
      imageset = ImageSetFactory.make_sweep(
        records[0].template, range(*image_range),
        format_class,
        records[0].beam, records[0].detector,
        records[0].goniometer, records[0].scan)

    else:

      # Get the filenames
      filenames = []
      for r in records:
        assert(r.template is None)
        filenames.append(r.filename)

      # make an imageset
      imageset = ImageSetFactory.make_imageset(filenames, format_class)
      for i, r in enumerate(records):
        imageset.set_beam(r.beam, i)
        imageset.set_detector(r.detector, i)
        imageset.set_goniometer(r.goniometer, i)
        imageset.set_scan(r.scan, i)

    # Return the imageset
    return imageset

  def _create_single_file_imageset(self, format_class, filename):
    ''' Create an imageset from a multi image file. '''
    from dxtbx.imageset import SingleFileReader, ImageSet, ImageSweep
    format_instance = format_class(filename)
    try:
      scan = format_instance.get_scan()
      if abs(scan.get_oscillation()[1]) > 0.0:
        return ImageSweep(SingleFileReader(format_instance))
    except Exception:
      pass
    return ImageSet(SingleFileReader(format_instance))


class DataBlockDictImporter(object):
  ''' A class to import a datablock from dictionary. '''

  def __init__(self, obj, check_format=True):
    ''' Get the datablocks from the dictionary. '''
    self.datablocks = self._load_datablocks(obj, check_format)

  def _load_datablocks(self, obj, check_format=True):
    ''' Create the datablock from a dictionary. '''
    from collections import OrderedDict
    from dxtbx.format.Registry import Registry
    from dxtbx.model import Beam, Detector, Goniometer, Scan
    from dxtbx.model import HierarchicalDetector
    from dxtbx.serialize.filename import load_path
    from dxtbx.imageset import ImageSetFactory

    # If we have a list, extract for each dictionary in the list
    if isinstance(obj, list):
      return [self._load_datablocks(dd, check_format) for dd in obj]
    elif not isinstance(obj, dict):
      raise RuntimeError('unknown datablock dictionary type')
    assert(obj['__id__'] == 'DataBlock')

    # Get the list of models
    blist = obj.get('beam', [])
    dlist = obj.get('detector', [])
    glist = obj.get('goniometer', [])
    slist = obj.get('scan', [])

    def load_models(obj):
      try:
        beam = Beam.from_dict(blist[obj['beam']])
      except Exception:
        beam = None
      try:
        dobj = dlist[obj['detector']]
        if 'hierarchy' in obj:
          detector = HierarchicalDetector.from_dict(dobj)
        else:
          detector = Detector.from_dict(dobj)
      except Exception:
        detector = None
      try:
        gonio = Goniometer.from_dict(glist[obj['goniometer']])
      except Exception:
        gonio = None
      try:
        scan = Scan.from_dict(slist[obj['scan']])
      except Exception:
        scan = None
      return beam, detector, gonio, scan

    # Loop through all the imagesets
    imagesets = []
    for imageset in obj['imageset']:
      ident = imageset['__id__']
      if ident == 'ImageSweep':
        beam, detector, gonio, scan = load_models(imageset)
        template = load_path(imageset['template'])
        i0, i1 = scan.get_image_range()
        imagesets.append(ImageSetFactory.make_sweep(
          template, range(i0, i1+1), None,
          beam, detector, gonio, scan, check_format))
      elif ident == 'ImageSet':
        filenames = [image['filename'] for image in imageset['images']]
        iset = ImageSetFactory.make_imageset(
          filenames, None, check_format)
        for i, image in enumerate(imageset['images']):
          beam, detector, gonio, scan = load_models(image)
          iset.set_beam(beam, i)
          iset.set_detector(detector, i)
          if goniometer:
            iset.set_goniometer(gonio, i)
          if scan:
            iset.set_scan(scan, i)
        imagesets.append(iset)
      else:
        raise RuntimeError('expected ImageSet/ImageSweep, got %s' % ident)

    # Return the datablock
    return DataBlock(imagesets)


class DataBlockImageSetImporter(object):
  ''' A class to import a datablock from imagesets. '''

  def __init__(self, imagesets):
    ''' Load a list of datablocks from imagesets. '''
    self.datablocks = []
    if not isinstance(imagesets, list):
      imagesets = [imagesets]
    for imageset in imagesets:
      try:
        self.datablocks[-1].append(imageset)
      except:
        self.datablocks.append(DataBlock([imageset]))


class DataBlockFactory(object):
  ''' Class for creating DataBlock instances'''

  @staticmethod
  def from_args(args, verbose=False, unhandled=None):
    ''' Try to load datablocks from any recognized format. '''

    if unhandled is None:
      unhandled = []
    unhandled1 = []

    # Try as image files
    datablocks = DataBlockFactory.from_filenames(args, verbose, unhandled1)

    # Try as serialized formats
    for filename in unhandled1:
      try:
        datablocks.extend(DataBlockFractory.from_serialized_format(filename))
        if verbose: print 'Loaded datablocks(s) from %s' % filename
      except Exception:
        unhandled.append(filename)

    # Return the datablocks
    return datablocks

  @staticmethod
  def from_filenames(filenames, verbose=False, unhandled=None):
    ''' Create a list of data blocks from a list of filenames. '''
    importer = DataBlockFilenameImporter(filenames, verbose)
    if unhandled is not None:
      unhandled.extend(importer.unhandled)
    return importer.datablocks

  @staticmethod
  def from_dict(obj, check_format=True):
    ''' Create a datablock from a dictionary. '''
    importer = DataBlockDictImporter(obj, check_format)
    return importer.datablocks

  @staticmethod
  def from_json(string, check_format=True):
    ''' Decode a datablock from JSON string. '''
    from dxtbx.serialize.load import _decode_dict
    import json
    return DataBlockFactory.from_dict(json.loads(
      string, object_hook=_decode_dict), check_format)

  @staticmethod
  def from_json_file(filename, check_format=True):
    ''' Decode a datablock from a JSON file. '''
    from os.path import dirname, abspath
    from dxtbx.serialize.filename import temp_chdir
    filename = abspath(filename)
    with temp_chdir(dirname(filename)):
      with open(filename, 'r') as infile:
        return DataBlockFactory.from_json(infile.read(), check_format)

  @staticmethod
  def from_pickle_file(filename):
    ''' Decode a datablock from a pickle file. '''
    import cPickle as pickle
    with open(filename, 'rb') as infile:
      obj = pickle.load(infile)
      if isinstance(obj, list):
        assert(all(isinstance(db, DataBlock) for db in obj))
      else:
        assert(isinstance(obj, DataBlock))
      return obj

  @staticmethod
  def from_imageset(imagesets):
    ''' Load a datablock from an imageset of list of imagesets. '''
    importer = DataBlockImageSetImporter(imagesets)
    return importer.datablocks

  @staticmethod
  def from_imageset_json_file(filename):
    ''' Load a datablock from a sweep file. '''
    from dxtbx.serialize import load
    from dxtbx.serialize.imageset import NullSweep
    from dxtbx.imageset import ImageSet, ImageSweep

    # Load the imageset and create a datablock from the filenames
    imageset = load.imageset(filename)
    return DataBlockFactory.from_imageset(imageset)

  @staticmethod
  def from_serialized_format(filename, check_format=True):
    ''' Load a datablock from serialized formats. '''

    # First try as JSON format
    try:
      return DataBlockFactory.from_json_file(filename, check_format)
    except Exception, e:
      pass

    # Now try as pickle format
    try:
      return DataBlockFactory.from_pickle_file(filename)
    except Exception:
      pass

    # Now try as imageset json files
    return DataBlockFactory.from_imageset_json_file(filename)

  @staticmethod
  def from_in_memory(images, indices=None):
    ''' Function to instantiate data block from in memory imageset. '''
    from dxtbx.imageset import MemImageSet
    return DataBlock([MemImageSet(images, indices)])

class DataBlockDumper(object):
  ''' Class to help in dumping datablock objects. '''

  def __init__(self, datablocks):
    ''' Initialise the list of data blocks. '''
    if isinstance(datablocks, DataBlock):
      self._datablocks = [datablocks]
    else:
      self._datablocks = datablocks

  def as_json(self, filename=None, compact=False):
    ''' Dump datablock as json. '''
    from os.path import splitext
    import json
    import cPickle as pickle
    ext = splitext(filename)[1]
    dictionary = [db.to_dict() for db in self._datablocks]
    if compact:
      json.dump(dictionary, open(filename, "w"),
        separators=(',',':'), ensure_ascii=True)
    else:
      json.dump(dictionary, open(filename, "w"),
        indent=2, ensure_ascii=True)

  def as_pickle(self, filename=None, **kwargs):
    ''' Dump datablock as pickle. '''
    import cPickle as pickle

    # Get the pickle string
    text = pickle.dumps(self._datablocks,
      protocol=pickle.HIGHEST_PROTOCOL)

    # Write the file
    if filename is not None:
      with open(filename, 'wb') as outfile:
        outfile.write(text)
    else:
      return text

  def as_file(self, filename, **kwargs):
    ''' Dump datablocks as file. '''
    from os.path import splitext
    ext = splitext(filename)[1]
    j_ext = ['.json']
    p_ext = ['.p', '.pkl', '.pickle']
    if ext.lower() in j_ext:
      return self.as_json(filename, **kwargs)
    elif ext.lower() in p_ext:
      return self.as_pickle(filename, **kwargs)
    else:
      ext_str = '|'.join(j_ext + p_ext)
      raise RuntimeError('expected extension {%s}, got %s' % (ext_str, ext))
