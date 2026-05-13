/**
 * Gemini Nano Banana Pro API Service
 * 
 * Handles integration with Google's Gemini Nano Banana Pro image generation API
 * Supports reference images, prompt engineering, and high-resolution texture generation
 */

export interface GenerateImageParams {
  prompt: string;
  referenceImages?: ImageData[];
  resolution?: [number, number];
  style?: 'photorealistic' | 'stylized' | 'artistic' | 'technical';
  lighting?: 'daylight' | 'studio' | 'natural' | 'dramatic';
  seed?: number;
  consistencyMode?: 'low' | 'medium' | 'high';
}

export interface ImageData {
  url?: string;
  base64?: string;
  data?: ArrayBuffer;
  width: number;
  height: number;
  mimeType: string;
}

export interface GenerationContext {
  objectType?: string;
  materialType?: string;
  previousTextures?: string[];
  neighboringChunks?: string[];
  sceneContext?: string;
}

export interface ValidationResult {
  valid: boolean;
  quality: number; // 0-1
  consistency: number; // 0-1
  issues: string[];
}

export class GeminiNanoBananaProService {
  private apiKey: string;
  private baseUrl: string = 'https://generativelanguage.googleapis.com/v1beta';
  private model: string = 'nano-banana-pro';
  
  constructor(apiKey?: string) {
    this.apiKey = apiKey || process.env.GEMINI_API_KEY || '';
    if (!this.apiKey) {
      console.warn('[GeminiNanoBananaPro] API key not provided. Set GEMINI_API_KEY environment variable.');
    }
  }

  /**
   * Generate texture image using Gemini Nano Banana Pro
   */
  async generateImage(params: GenerateImageParams): Promise<ImageData> {
    if (!this.apiKey) {
      throw new Error('Gemini API key not configured');
    }

    try {
      // Build enhanced prompt
      const enhancedPrompt = this.enhancePrompt(params.prompt, {
        style: params.style,
        lighting: params.lighting,
        consistencyMode: params.consistencyMode
      });

      // Prepare request body
      const requestBody: any = {
        contents: [{
          role: 'user',
          parts: [
            { text: enhancedPrompt }
          ]
        }],
        generationConfig: {
          temperature: 0.7,
          topK: 40,
          topP: 0.95,
          maxOutputTokens: 8192,
        }
      };

      // Add reference images if provided
      if (params.referenceImages && params.referenceImages.length > 0) {
        for (const refImage of params.referenceImages) {
          const imagePart: any = {
            inlineData: {
              mimeType: refImage.mimeType || 'image/png',
              data: refImage.base64 || await this.imageToBase64(refImage)
            }
          };
          requestBody.contents[0].parts.push(imagePart);
        }
      }

      // Make API request
      const response = await fetch(
        `${this.baseUrl}/models/${this.model}:generateContent?key=${this.apiKey}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestBody)
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(`Gemini API error: ${error.error?.message || 'Unknown error'}`);
      }

      const data = await response.json();
      
      // Extract image from response
      // Note: Actual API response structure may vary - adjust based on real API docs
      const imageData = this.parseImageResponse(data);
      
      return imageData;
    } catch (error) {
      console.error('[GeminiNanoBananaPro] Generation error:', error);
      throw error;
    }
  }

  /**
   * Enhance prompt with context and style information
   */
  enhancePrompt(
    basePrompt: string,
    context?: {
      style?: string;
      lighting?: string;
      consistencyMode?: string;
    }
  ): string {
    let enhanced = basePrompt;

    // Add style information
    if (context?.style) {
      enhanced += `\nStyle: ${context.style}, professional quality, high detail`;
    }

    // Add lighting information
    if (context?.lighting) {
      enhanced += `\nLighting: ${context.lighting}, realistic shadows and highlights`;
    }

    // Add consistency instructions
    if (context?.consistencyMode === 'high') {
      enhanced += `\nImportant: Maintain visual consistency with reference images. Match colors, patterns, and material properties exactly.`;
    }

    // Add quality instructions
    enhanced += `\nQuality: 4K resolution, photorealistic, seamless tiling where appropriate, proper UV mapping`;

    return enhanced;
  }

  /**
   * Validate generated image
   */
  async validateImage(image: ImageData): Promise<ValidationResult> {
    const issues: string[] = [];
    let quality = 1.0;
    let consistency = 1.0;

    // Check resolution
    if (image.width < 1024 || image.height < 1024) {
      issues.push('Resolution too low for texture use');
      quality -= 0.2;
    }

    // Check if image data exists
    if (!image.url && !image.base64 && !image.data) {
      issues.push('No image data available');
      quality = 0;
    }

    // Additional validation can be added here
    // (e.g., image quality analysis, consistency checking, etc.)

    return {
      valid: issues.length === 0,
      quality: Math.max(0, quality),
      consistency: Math.max(0, consistency),
      issues
    };
  }

  /**
   * Convert image to base64
   */
  private async imageToBase64(image: ImageData): Promise<string> {
    if (image.base64) {
      return image.base64;
    }

    if (image.url) {
      const response = await fetch(image.url);
      const blob = await response.blob();
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => {
          const base64 = reader.result as string;
          resolve(base64.split(',')[1]); // Remove data:image/png;base64, prefix
        };
        reader.onerror = reject;
        reader.readAsDataURL(blob);
      });
    }

    if (image.data) {
      const blob = new Blob([image.data], { type: image.mimeType });
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => {
          const base64 = reader.result as string;
          resolve(base64.split(',')[1]);
        };
        reader.onerror = reject;
        reader.readAsDataURL(blob);
      });
    }

    throw new Error('No image data available for conversion');
  }

  /**
   * Parse image response from API
   * Note: This is a placeholder - actual API response structure may differ
   */
  private parseImageResponse(data: any): ImageData {
    // TODO: Parse actual API response structure
    // This is a placeholder implementation
    
    // Example structure (adjust based on real API):
    // const imagePart = data.candidates[0]?.content?.parts?.find((p: any) => p.inlineData);
    // if (imagePart?.inlineData) {
    //   return {
    //     base64: imagePart.inlineData.data,
    //     width: 4096,
    //     height: 4096,
    //     mimeType: imagePart.inlineData.mimeType
    //   };
    // }

    // For now, return a placeholder
    return {
      base64: '',
      width: 4096,
      height: 4096,
      mimeType: 'image/png'
    };
  }

  /**
   * Handle API errors with retry logic
   */
  private async retryWithBackoff<T>(
    fn: () => Promise<T>,
    maxRetries: number = 3,
    initialDelay: number = 1000
  ): Promise<T> {
    let lastError: Error | null = null;
    
    for (let attempt = 0; attempt < maxRetries; attempt++) {
      try {
        return await fn();
      } catch (error: any) {
        lastError = error;
        
        // Check if error is retryable
        if (error.message?.includes('rate limit') || error.message?.includes('quota')) {
          const delay = initialDelay * Math.pow(2, attempt);
          console.log(`[GeminiNanoBananaPro] Retrying after ${delay}ms (attempt ${attempt + 1}/${maxRetries})`);
          await new Promise(resolve => setTimeout(resolve, delay));
          continue;
        }
        
        // Non-retryable error
        throw error;
      }
    }
    
    throw lastError || new Error('Max retries exceeded');
  }
}

export default GeminiNanoBananaProService;

