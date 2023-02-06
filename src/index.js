const express = require('express');
const app = express();
const multer = require('multer');

const imageAnalysis = require('./imageAnalysis.js');

const upload = multer({
  fileFilter: async (req, file, cb) => {
    if (!file.mimetype.match(/jpe|jpeg|png|gif$i/)) {
      return cb(new Error('File type is not supported'), false);
    }
    let resp=await imageAnalysis(file);
    cb(resp, true);
  }
});

app.post('/upload', upload.single('image'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ message: 'Please provide an image',"pass": false });
  }

  res.status(200).json({
    "message": "Your document quality is good",
    "quality": "99",
    "pass": true
  });
});

app.use((error, req, res, next) => {
  res.status(400).json({ message: error.message,"pass": false });
});

app.listen(3000, () => {
  console.log('Image API listening on port 3000');
});
