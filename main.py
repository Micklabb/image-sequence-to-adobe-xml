import xml.etree.ElementTree as ET
from PIL import Image
import os

class Clip:
    def __init__(self, id, path, start, end):
        self.id = id
        self.path = path
        self.imgfile = Image.open(self.path)
        self.name = os.path.basename(path)
        self.width = self.imgfile.width
        self.height = self.imgfile.height
        self.scale = 100
        self.start = start
        self.end = end

    def scaleToFitSequence(self, seq_width, seq_height):
        self.scale = min( seq_width/self.width, seq_height/self.height) * 100

    def setScaleTo(self, scale):
        self.scale = scale

    def getXML(self):
        sub = ET.parse('sub_template.xml')
        clipitem = sub.getroot()
        clipitem.set('id', 'clipitem-{}'.format(self.id))
        clipitem.find('masterclipid').text = 'masterclip-{}'.format(self.id)
        clipitem.find('name').text = self.name
        clipitem.find('start').text = str(self.start)
        clipitem.find('end').text = str(self.end)
        clipitem.find('out').text = str(90000 + self.end)
        clipitem.find('pproTicksIn').text = str(int(((self.start/25)+3600)*254016000000))
        clipitem.find('pproTicksOut').text = str(int(((self.end/25)+3600)*254016000000))

        file = clipitem.find('file')
        file.set('id', 'file-{}'.format(self.id))
        file.find('name').text = self.name
        file.find('pathurl').text = self.path

        media = file.find('./media/video/samplecharacteristics')
        media.find('width').text = str(self.width)
        media.find('height').text = str(self.height)

        clipitem.find('./filter/effect/parameter/value').text = str(int(self.scale))

        return clipitem

class Sequence:
    def __init__(self, name, folder):
        self.name = name
        self.width = 1920
        self.height = 1080
        self.folder = folder
        self.duration = 100000
        self.files = self.getFiles()
        self.ids = self.setIds(self.files)
        self.timings = self.setTimings(10, self.files)

    def getFiles(self):
        for (dirpath, dirnames, filenames) in os.walk(self.folder):
            files = filenames
        return list(map(lambda x: "{}/{}".format(self.folder, x), files))

    def setIds(self, l):
        return range(1, len(l))

    def setTimings(self, frames, l):
        return ([x*frames for x in range(len(l))], [x*frames+frames for x in range(len(l))])

    def getXML(self):
        main = ET.parse('template.xml')
        xmeml = main.getroot()
        sequence = xmeml.find('sequence')
        sequence.find('duration').text = str(self.duration)
        sequence.find('name').text = self.name

        export = sequence.find('./media/video/format/samplecharacteristics')
        export.find('width').text = str(self.width)
        export.find('height').text = str(self.height)

        batch = list(zip(self.ids, self.files, *self.timings))
        track = main.find("./sequence/media/video/track")

        for item in batch:
            clip = Clip(*item)
            clip.scaleToFitSequence(self.width, self.height)
            xml = clip.getXML()
            track.append(xml)

        return main

if __name__ == "__main__":
    project_name = 'test'
    image_folder = 'watchfolder/img'

    project = Sequence(project_name, image_folder)
    output = project.getXML()

    output.write('watchfolder/output.xml')
