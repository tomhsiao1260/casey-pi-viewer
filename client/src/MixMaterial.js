import { ShaderMaterial, Vector2 } from "three";

export class MixMaterial extends ShaderMaterial {
  constructor(params) {
    super({

      uniforms: {
        uSegmentTexture : { value: null },
        uVolumeTexture : { value: null }
      },

      vertexShader: /* glsl */ `
        varying vec2 vUv;
        void main() {
          vUv = uv;
          gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
      }
      `,

      fragmentShader: /* glsl */ `
        varying vec2 vUv;
        uniform sampler2D uSegmentTexture;
        uniform sampler2D uVolumeTexture;

        void main() {
          vec4 segmentColor = texture2D(uSegmentTexture, vUv);
          vec4 volumeColor = texture2D(uVolumeTexture, vUv);

          if (volumeColor.g < 0.05 )
            gl_FragColor = segmentColor;
          else
            gl_FragColor = volumeColor;
        }
      `
    });

    this.setValues(params);
  }
}
