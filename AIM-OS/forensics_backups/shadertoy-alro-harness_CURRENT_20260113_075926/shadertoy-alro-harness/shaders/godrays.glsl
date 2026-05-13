#version 300 es
precision highp float;

uniform vec2 uResolution;
uniform sampler2D uScene; // rgba, alpha = cloud transmittance (1 = clear, 0 = fully blocked)

uniform vec2 uLightUv; // screen-space [0..1]
uniform vec3 uLightColor; // rgb in [0..1]

uniform float uIntensity;
uniform float uDensity;
uniform float uDecay;
uniform float uWeight;
uniform int uSamples;
uniform float uSourceRadius; // uv radius of the sun/moon disk

out vec4 outColor;

vec3 toLinear(vec3 srgb) {
  return pow(max(srgb, vec3(0.0)), vec3(2.2));
}

vec3 toSrgb(vec3 linear) {
  return pow(max(linear, vec3(0.0)), vec3(1.0 / 2.2));
}

void main() {
  vec2 uv = gl_FragCoord.xy / uResolution;
  vec4 base = texture(uScene, uv);

  vec3 colorLinear = toLinear(base.rgb);

  if (uIntensity <= 0.0 || uSamples <= 0) {
    outColor = vec4(toSrgb(colorLinear), 1.0);
    return;
  }

  // If the light is off-screen, skip the pass.
  if (any(lessThan(uLightUv, vec2(-0.25))) || any(greaterThan(uLightUv, vec2(1.25)))) {
    outColor = vec4(toSrgb(colorLinear), 1.0);
    return;
  }

  vec2 delta = (uLightUv - uv) * (uDensity / float(uSamples));
  vec2 coord = uv;

  float illuminationDecay = 1.0;
  float sum = 0.0;

  const int MAX_SAMPLES = 128;
  for (int i = 0; i < MAX_SAMPLES; i++) {
    if (i >= uSamples) break;
    coord += delta;
    float distToLight = distance(coord, uLightUv);
    float source = 1.0 - smoothstep(uSourceRadius, uSourceRadius * 1.25, distToLight);
    float transmittance = clamp(texture(uScene, coord).a, 0.0, 1.0);
    sum += (source * transmittance) * illuminationDecay;
    illuminationDecay *= uDecay;
  }

  float rays = sum * uWeight * uIntensity;
  colorLinear += uLightColor * rays;

  outColor = vec4(toSrgb(colorLinear), 1.0);
}
