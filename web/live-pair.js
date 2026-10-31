/* Apple MakerNote tag 17 + QuickTime identifier pairing, as used by makelive.
 * Image metadata is created from scratch: no camera identity, GPS or donor data.
 */
export function pairedJpeg(jpeg, assetId) {
  if (!/^[a-f0-9-]{36}$/i.test(assetId) || jpeg[0] !== 255 || jpeg[1] !== 216) {
    throw new Error('Expected a JPEG and UUID');
  }
  const maker = new Uint8Array(70);
  const m = new DataView(maker.buffer);
  maker.set(new TextEncoder().encode('Apple iOS\0\0\x01MM'));
  m.setUint16(14, 1);
  m.setUint16(16, 17);
  m.setUint16(18, 2);
  m.setUint32(20, 37);
  m.setUint32(24, 32);
  maker.set(new TextEncoder().encode(assetId), 32);
  const tiff = new Uint8Array(44 + maker.length);
  const t = new DataView(tiff.buffer);
  tiff.set([77, 77, 0, 42]);
  t.setUint32(4, 8);
  t.setUint16(8, 1);
  t.setUint16(10, 0x8769); // Exif IFD pointer.
  t.setUint16(12, 4);
  t.setUint32(14, 1);
  t.setUint32(18, 26);
  t.setUint16(26, 1);
  t.setUint16(28, 0x927c); // MakerNote.
  t.setUint16(30, 7);
  t.setUint32(32, maker.length);
  t.setUint32(36, 44);
  tiff.set(maker, 44);
  const exif = new Uint8Array(6 + tiff.length);
  exif.set([69, 120, 105, 102, 0, 0]);
  exif.set(tiff, 6);
  const segment = new Uint8Array(exif.length + 4);
  segment.set([255, 225]);
  new DataView(segment.buffer).setUint16(2, exif.length + 2);
  segment.set(exif, 4);
  const result = new Uint8Array(jpeg.length + segment.length);
  result.set(jpeg.subarray(0, 2));
  result.set(segment, 2);
  result.set(jpeg.subarray(2), 2 + segment.length);
  return result;
}

export const packagePlist = `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict><key>PFVideoComplementMetadataVersionKey</key><string>1</string></dict></plist>`;
