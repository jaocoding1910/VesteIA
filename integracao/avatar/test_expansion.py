"""Checks geometry and actual preservation, without claiming GPU visual QA."""
import base64
import importlib.util
import io
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import unittest
import numpy as np
from PIL import Image

spec = importlib.util.spec_from_file_location("expansion", Path(__file__).with_name("engine.py"))
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)


class ExpansionTests(unittest.TestCase):
    def test_landscape_portrait_and_square_preserve_aspect_and_face(self):
        for size in ((400, 600), (600, 400), (512, 512), (900, 1600)):
            yy, xx = np.mgrid[:size[1], :size[0]]
            source = Image.fromarray(np.stack((xx % 255, yy % 255, (xx+yy) % 255), axis=-1).astype('uint8'))
            face = (size[0]//3, size[1]//5, size[0]//5, size[1]//6)
            canvas, mask, reference = engine.prepare_photo(source, face)
            assert canvas.size == mask.size == (512, 768)
            assert min(reference.size) > 0
            known = np.asarray(mask) == 0
            assert known.sum() > 500
            # A simulated model changes everything; final composition restores source.
            composed = Image.composite(Image.new('RGB', canvas.size, 'red'), canvas, mask)
            np.testing.assert_array_equal(np.asarray(composed)[known], np.asarray(canvas)[known])
            assert mask.getextrema() == (0, 255)

    def test_generation_uses_entire_canvas_and_no_template(self):
        image = Image.new('RGB', (400, 600), (38, 92, 127))
        stream = io.BytesIO(); image.save(stream, format='PNG')
        calls = []
        def pipeline(**kwargs):
            calls.append(kwargs)
            return SimpleNamespace(images=[Image.new('RGB', (512, 768), 'red')], nsfw_content_detected=[False])
        class Generator:
            def __init__(self, **kwargs): pass
            def manual_seed(self, seed): return self
        with patch.object(engine, 'face_box', return_value=(140, 110, 90, 90)), patch.object(engine, 'load_pipeline', return_value=pipeline), patch.dict('sys.modules', {'torch': SimpleNamespace(Generator=Generator)}):
            result = engine.generate({'selfie': base64.b64encode(stream.getvalue()).decode(), 'template': 'masculino'})
        assert result['body_source'] == 'photo_outpaint'
        assert calls[0]['mask_image'].getpixel((256, 750)) == 255
        assert calls[0]['image'].size == (512, 768)
        assert calls[0]['strength'] == 1.0
        output = Image.open(io.BytesIO(base64.b64decode(result['image'])))
        assert output.size == (512, 768)

    def test_invalid_image_rejected(self):
        with self.assertRaises(ValueError): engine.decode('not base64')
        with self.assertRaises(ValueError): engine.decode(None)

    def test_safety_rejection_is_kept(self):
        image=Image.new('RGB',(256,256),'gray'); stream=io.BytesIO();image.save(stream,format='PNG')
        class Generator:
            def __init__(self, **kwargs): pass
            def manual_seed(self, seed): return self
        pipeline=lambda **kwargs: SimpleNamespace(images=[], nsfw_content_detected=[True])
        with patch.object(engine,'face_box',return_value=(80,60,64,64)), patch.object(engine,'load_pipeline',return_value=pipeline), patch.dict('sys.modules',{'torch':SimpleNamespace(Generator=Generator)}):
            with self.assertRaises(ValueError):engine.generate({'selfie':base64.b64encode(stream.getvalue()).decode(),'template':'masculino'})


if __name__ == '__main__': unittest.main()
