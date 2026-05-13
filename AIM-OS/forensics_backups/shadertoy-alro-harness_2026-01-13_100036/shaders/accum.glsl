#version 300 es
precision highp float;

uniform vec2 uResolution;
uniform sampler2D uCurrent;
uniform sampler2D uHistory;

uniform float uAlpha; // EMA blend factor in [0,1]
uniform int uReset; // 1 = reset history to current
uniform int uUseReprojection; // 1 = directional reprojection (rotation-only)

uniform vec3 uTargetDirCur;
uniform vec3 uTargetDirPrev;
uniform float uFovDeg;

out vec4 outColor;

vec3 rayDirection(float fieldOfViewDeg, vec2 fragCoord, vec2 resolution) {
  vec2 xy = fragCoord - resolution / 2.0;
  float z = (0.5 * resolution.y) / tan(radians(fieldOfViewDeg) / 2.0);
  return normalize(vec3(xy, -z));
}

// Matches the al-ro lookAt() (camera position does not matter for the returned basis).
mat3 lookAtDir(vec3 targetDir, vec3 up) {
  vec3 zaxis = normalize(targetDir);
  vec3 xaxis = normalize(cross(zaxis, up));
  vec3 yaxis = cross(xaxis, zaxis);
  return mat3(xaxis, yaxis, -zaxis);
}

vec2 dirToFragCoord(vec3 rayDirCam, float fieldOfViewDeg, vec2 resolution) {
  float z = (0.5 * resolution.y) / tan(radians(fieldOfViewDeg) / 2.0);
  // rayDirCam ~= normalize(vec3(xy, -z))
  // => xy = (-z / rayDirCam.z) * rayDirCam.xy
  float denom = rayDirCam.z;
  // In this camera convention, forward rays have negative z. Clamp away from 0 without flipping sign.
  float k = (-z) / min(-1e-6, denom);
  vec2 xy = k * rayDirCam.xy;
  return xy + resolution / 2.0;
}

void main() {
  vec2 fragCoord = gl_FragCoord.xy;
  vec2 uv = fragCoord / uResolution;

  vec4 current = texture(uCurrent, uv);

  if (uReset != 0) {
    outColor = current;
    return;
  }

  vec2 uvPrev = uv;
  bool validPrev = true;

  if (uUseReprojection != 0) {
    vec3 up = vec3(0.0, 1.0, 0.0);

    vec3 rayCamCur = rayDirection(uFovDeg, fragCoord, uResolution);
    mat3 viewCur = lookAtDir(uTargetDirCur, up);
    vec3 rayWorld = normalize(viewCur * rayCamCur);

    mat3 viewPrev = lookAtDir(uTargetDirPrev, up);
    vec3 rayCamPrev = transpose(viewPrev) * rayWorld;

    // In this camera convention, forward rays have negative z.
    // If the previous ray points behind the camera, treat as disocclusion and skip history.
    if (rayCamPrev.z < -1e-4) {
      vec2 fragPrev = dirToFragCoord(rayCamPrev, uFovDeg, uResolution);
      uvPrev = fragPrev / uResolution;
    } else {
      validPrev = false;
    }

    if (validPrev) {
      if (any(lessThan(uvPrev, vec2(0.0))) || any(greaterThan(uvPrev, vec2(1.0)))) {
        validPrev = false;
      }
    }

    // If reprojection can't find valid history (newly revealed pixels), avoid sampling mismatched history.
    if (!validPrev) {
      outColor = current;
      return;
    }
  }

  vec4 history = texture(uHistory, uvPrev);

  // Motion-aware blend: when reprojection moves a lot, trust the current frame more to reduce "laggy" chunks.
  float alpha = clamp(uAlpha, 0.0, 1.0);
  if (uUseReprojection != 0) {
    float motion = length(uvPrev - uv);
    float w = smoothstep(0.02, 0.18, motion);
    alpha = mix(alpha, 1.0, w);
  }

  outColor = mix(history, current, alpha);
}
