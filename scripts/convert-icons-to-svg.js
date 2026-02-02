/**
 * Improved Icon PNG to SVG Converter (v2)
 * Pre-processes PNGs to extract teal color channel, then traces to SVG
 * Optimizes output with SVGO
 */

const { Jimp } = require('jimp');
const potrace = require('potrace');
const fs = require('fs');
const path = require('path');
const { optimize } = require('svgo');

// Directories
const SOURCE_DIR = 'C:\\Users\\ryanh\\.gemini\\antigravity\\brain\\03e28c61-d0de-4f47-a260-e1069a15d13c';
const OUTPUT_DIR = path.join(__dirname, '..', 'web', 'assets', 'icons', 'svg');
const PROCESSED_DIR = path.join(__dirname, '..', 'web', 'assets', 'icons', 'processed');

// Teal color RGB values (approximately #00E5CC)
const TEAL_R = 0;
const TEAL_G = 229;
const TEAL_B = 204;
const COLOR_TOLERANCE = 60;

// SVGO configuration for minimal clean SVGs
const SVGO_CONFIG = {
    multipass: true,
    plugins: [
        'preset-default',
        'removeDimensions',
        {
            name: 'removeAttrs',
            params: {
                attrs: ['fill-rule']
            }
        }
    ]
};

async function preprocessImage(inputPath, outputPath) {
    const image = await Jimp.read(inputPath);
    const { width, height } = image;
    
    // Create a black and white version based on teal color detection
    for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
            const color = image.getPixelColor(x, y);
            const r = (color >> 24) & 0xFF;
            const g = (color >> 16) & 0xFF;
            const b = (color >> 8) & 0xFF;
            const a = color & 0xFF;
            
            // Check if this pixel is close to our teal color
            const isTeal = Math.abs(r - TEAL_R) < COLOR_TOLERANCE &&
                          Math.abs(g - TEAL_G) < COLOR_TOLERANCE &&
                          Math.abs(b - TEAL_B) < COLOR_TOLERANCE &&
                          a > 128;
            
            if (isTeal) {
                // Make it black (for potrace)
                image.setPixelColor(0x000000FF, x, y);
            } else {
                // Make it white (background)
                image.setPixelColor(0xFFFFFFFF, x, y);
            }
        }
    }
    
    await image.write(outputPath);
    return outputPath;
}

async function traceToSvg(imagePath) {
    return new Promise((resolve, reject) => {
        potrace.trace(imagePath, {
            color: '#00E5CC',
            optTolerance: 0.4,
            turdSize: 5,
            alphaMax: 1.0,
            optCurve: true,
            threshold: 200
        }, (err, svg) => {
            if (err) reject(err);
            else resolve(svg);
        });
    });
}

function optimizeSvg(svg) {
    const result = optimize(svg, SVGO_CONFIG);
    return result.data;
}

function extractPathData(svg) {
    const match = svg.match(/d="([^"]+)"/);
    return match ? match[1] : null;
}

async function main() {
    // Ensure directories exist
    for (const dir of [OUTPUT_DIR, PROCESSED_DIR]) {
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
        }
    }
    
    // Find all PNG icon files
    const files = fs.readdirSync(SOURCE_DIR)
        .filter(f => f.endsWith('.png') && f.includes('_icon') && !f.includes('device_icons_set'));
    
    console.log(`Found ${files.length} icon files to convert\n`);
    
    const results = {
        success: [],
        failed: [],
        pathData: {}
    };
    
    for (const file of files) {
        const inputPath = path.join(SOURCE_DIR, file);
        const baseName = file.replace(/_\d+\.png$/, '').replace(/_icon$/, '');
        const processedPath = path.join(PROCESSED_DIR, `${baseName}_processed.png`);
        const svgPath = path.join(OUTPUT_DIR, `${baseName}.svg`);
        
        try {
            process.stdout.write(`[${results.success.length + 1}/${files.length}] ${baseName}... `);
            
            // Step 1: Preprocess image
            await preprocessImage(inputPath, processedPath);
            
            // Step 2: Trace to SVG
            let svg = await traceToSvg(processedPath);
            
            // Step 3: Optimize SVG
            svg = optimizeSvg(svg);
            
            // Step 4: Extract path data
            const pathData = extractPathData(svg);
            
            // Step 5: Save SVG
            fs.writeFileSync(svgPath, svg);
            
            if (pathData) {
                results.pathData[baseName] = pathData;
                console.log('✓');
                results.success.push({ name: baseName, svgSize: svg.length, pathSize: pathData.length });
            } else {
                console.log('⚠ No path');
                results.success.push({ name: baseName, svgSize: svg.length, pathSize: 0 });
            }
        } catch (err) {
            console.log(`✗ ${err.message}`);
            results.failed.push({ file: baseName, error: err.message });
        }
    }
    
    console.log(`\n${'='.repeat(60)}`);
    console.log(`Conversion complete!`);
    console.log(`  Success: ${results.success.length}`);
    console.log(`  Failed: ${results.failed.length}`);
    console.log(`  Output: ${OUTPUT_DIR}`);
    
    // Statistics
    const avgPathSize = results.success.reduce((sum, s) => sum + s.pathSize, 0) / results.success.length;
    console.log(`  Avg path size: ${Math.round(avgPathSize)} chars`);
    
    // Write path data JSON
    const pathDataFile = path.join(OUTPUT_DIR, '_icon-paths.json');
    fs.writeFileSync(pathDataFile, JSON.stringify(results.pathData, null, 2));
    console.log(`\nPath data saved to: ${pathDataFile}`);
    
    // Report failures
    if (results.failed.length > 0) {
        console.log('\nFailed:');
        results.failed.forEach(f => console.log(`  - ${f.file}: ${f.error}`));
    }
    
    // Clean up processed images
    console.log('\nCleaning up processed images...');
    fs.readdirSync(PROCESSED_DIR).forEach(f => {
        fs.unlinkSync(path.join(PROCESSED_DIR, f));
    });
    fs.rmdirSync(PROCESSED_DIR);
    console.log('Done!');
}

main().catch(console.error);
