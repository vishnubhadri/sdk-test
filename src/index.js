const express = require('express');
const app = express();
const multer = require('multer');
const upload = multer({
  fileFilter: (req, file, cb) => {
    if (!file.mimetype.match(/jpe|jpeg|png|gif$i/)) {
      return cb(new Error('File type is not supported'), false);
    }
    cb(null, true);
  }
});

app.post('/upload', upload.single('image'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'Please provide an image' });
  }

  res.status(200).json({ message: 'Image received' });
});

app.use((error, req, res, next) => {
  res.status(400).json({ error: error.message });
});

app.listen(3000, () => {
  console.log('Image API listening on port 3000');
});
