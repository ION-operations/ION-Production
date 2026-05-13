precision highp float;

uniform sampler2D uTexture;
uniform float brightness;

varying vec2 vUv;

void main() {
    vec3 color = texture2D(uTexture, vUv).rgb;
    color *= brightness;
    
    // Subtle tone mapping
    color = color / (1.0 + color);
    
    gl_FragColor = vec4(color, 1.0);
}

