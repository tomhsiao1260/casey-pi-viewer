import { ShaderMaterial, Vector2, DoubleSide } from "three";

export class MaskMaterial extends ShaderMaterial {
  constructor(params) {
    super({
      transparent: true,
      side: DoubleSide,

      uniforms: {
        uTexture : { value: null }
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
        uniform sampler2D uTexture;

        void main() {
          gl_FragColor = texture2D(uTexture, vUv);
        }
      `
    });

    this.setValues(params);
  }
}
