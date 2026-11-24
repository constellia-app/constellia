import 'dart:ui' as ui;

import 'package:flutter/rendering.dart';
import 'package:flutter/widgets.dart';
import 'package:share_plus/share_plus.dart';

Future<void> shareAnnotatedPhoto(GlobalKey photoKey, int width) async {
  final boundary = photoKey.currentContext!.findRenderObject() as RenderRepaintBoundary;
  final image = await boundary.toImage(pixelRatio: width / boundary.size.width);
  final png = await image.toByteData(format: ui.ImageByteFormat.png);
  await SharePlus.instance.share(ShareParams(
    files: [XFile.fromData(png!.buffer.asUint8List(), mimeType: 'image/png', name: 'constellia.png')],
    text: 'Mon ciel, analysé par Constellia',
  ));
}
