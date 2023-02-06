const tf = require('@tensorflow/tfjs');
const sharp = require('sharp');

async function analyzeImage(fileBuffer) {
    const image = sharp(fileBuffer);
    const imageData = await image.metadata();

    const imageTensor = tf.browser.fromPixels(imageData, 3);
    const resizedImage = tf.image.resizeBilinear(imageTensor, [224, 224]);

    const prediction = await model.predict(resizedImage);
    console.log(`Image Quality Score: ${prediction[0]}`);
    console.log(`Quality Defects:`);
    console.log(`Blurry: ${prediction[1]}`);
    console.log(`Dark: ${prediction[2]}`);
    console.log(`Faint: ${prediction[3]}`);
    console.log(`Noisy: ${prediction[4]}`);
    console.log(`Text Too Small: ${prediction[5]}`);

    return {
        "quality_score": prediction[0],
        "quality": {
            "defect_blurry": prediction[1],
            "defect_dark": prediction[2],
            "defect_faint": prediction[3],
            "defect_noisy": prediction[4],
            "defect_text_too_small": prediction[5],
        }
    }
}

export default analyzeImage;