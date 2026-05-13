/**
 * Screenshot Capture Service
 * Captures screenshots and extracts regions
 */

const { desktopCapturer, screen } = require('electron');
const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

class ScreenshotService {
  /**
   * Capture full screen AFTER overlay closes
   * User has already selected the region they want
   */
  async captureScreen() {
    try {
      const primaryDisplay = screen.getPrimaryDisplay();
      
      const sources = await desktopCapturer.getSources({
        types: ['screen'],
        thumbnailSize: {
          width: primaryDisplay.size.width,
          height: primaryDisplay.size.height
        }
      });
      
      if (sources.length === 0) {
        throw new Error('No screen sources available');
      }
      
      // Return full screen screenshot as PNG buffer
      return sources[0].thumbnail.toPNG();
    } catch (error) {
      throw new Error(`Failed to capture screen: ${error.message}`);
    }
  }

  /**
   * Crop selected region from full screenshot
   */
  async extractRegion(fullScreenshot, rectangle) {
    try {
      const croppedRegion = await sharp(fullScreenshot)
        .extract({
          left: rectangle.x,
          top: rectangle.y,
          width: rectangle.width,
          height: rectangle.height
        })
        .png()
        .toBuffer();
      
      return croppedRegion;
    } catch (error) {
      throw new Error(`Failed to extract region: ${error.message}`);
    }
  }

  /**
   * Complete flow: Capture screen and crop region
   */
  async captureAndCrop(rectangle) {
    // Step 1: Capture full screen
    const fullScreenshot = await this.captureScreen();
    
    // Step 2: Crop selected region
    const croppedRegion = await this.extractRegion(fullScreenshot, rectangle);
    
    return {
      fullScreenshot,
      croppedRegion,
      rectangle
    };
  }

  /**
   * Save template to disk
   */
  async saveTemplate(templateData, metadata) {
    try {
      const templatesDir = path.join(__dirname, '..', 'templates');
      
      // Create templates directory if it doesn't exist
      if (!fs.existsSync(templatesDir)) {
        fs.mkdirSync(templatesDir, { recursive: true });
      }
      
      // Create template subdirectory
      const templateName = metadata.name.replace(/[^a-zA-Z0-9]/g, '-').toLowerCase();
      const templateDir = path.join(templatesDir, templateName);
      if (!fs.existsSync(templateDir)) {
        fs.mkdirSync(templateDir, { recursive: true });
      }
      
      // Convert base64 to Buffer if needed
      let croppedBuffer = templateData.croppedRegion;
      if (typeof croppedBuffer === 'string') {
        croppedBuffer = Buffer.from(croppedBuffer, 'base64');
      }
      
      // Save image
      const imagePath = path.join(templateDir, `${metadata.theme}.png`);
      fs.writeFileSync(imagePath, croppedBuffer);
      
      // Save metadata
      const metadataPath = path.join(templateDir, 'metadata.json');
      fs.writeFileSync(metadataPath, JSON.stringify({
        id: `${templateName}-${metadata.theme}`,
        name: metadata.name,
        theme: metadata.theme,
        rectangle: templateData.rectangle,
        screenshotBounds: {
          x: 0,
          y: 0,
          width: templateData.rectangle.width,
          height: templateData.rectangle.height
        },
        metadata: {
          os: process.platform,
          createdAt: new Date().toISOString()
        },
        createdAt: new Date().toISOString()
      }, null, 2));
      
      return {
        success: true,
        templatePath: imagePath,
        metadataPath: metadataPath,
        templateId: `${templateName}-${metadata.theme}`
      };
    } catch (error) {
      throw new Error(`Failed to save template: ${error.message}`);
    }
  }
}

module.exports = new ScreenshotService();

