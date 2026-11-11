import 'dart:math';

import 'package:flutter/material.dart';

import 'analysis.dart';
import 'constellation_names.dart';
import 'style.dart';

const starSize = 44.0;
const computedOpacity = 0.5;
const labelHeight = 20.0;

class AnnotatedPhoto extends StatelessWidget {
  final Analysis analysis;

  const AnnotatedPhoto(this.analysis, {super.key});

  @override
  Widget build(BuildContext context) {
    return AspectRatio(
      aspectRatio: analysis.width / analysis.height,
      child: LayoutBuilder(builder: (context, size) {
        final scale = size.maxWidth / analysis.width;
        return Stack(
          children: [
            Positioned.fill(child: Image.memory(analysis.photo, fit: BoxFit.fill)),
            Positioned.fill(child: CustomPaint(painter: LinesPainter(analysis.lines, scale))),
            for (final star in analysis.computed) PlacedStar(star, scale, opacity: computedOpacity),
            for (final star in analysis.stars) PlacedStar(star, scale),
            for (final constellation in analysis.constellations)
              if (analysis.confirmed.contains(constellation.name))
                Positioned(
                  left: constellation.box.left * scale,
                  top: constellation.box.top * scale - labelHeight,
                  child: Text(frenchName(constellation.name).toUpperCase(), style: constellationNameStyle),
                ),
          ],
        );
      }),
    );
  }
}

class PlacedStar extends StatelessWidget {
  final NamedStar star;
  final double scale;
  final double opacity;

  const PlacedStar(this.star, this.scale, {super.key, this.opacity = 1});

  @override
  Widget build(BuildContext context) {
    return Positioned(
      left: star.position.x * scale - starSize / 2,
      top: star.position.y * scale - starSize / 2,
      width: starSize,
      height: starSize,
      child: Opacity(opacity: opacity, child: Image.asset(starImage)),
    );
  }
}

class LinesPainter extends CustomPainter {
  final List<ConstellationLine> lines;
  final double scale;

  LinesPainter(this.lines, this.scale);

  Offset onScreen(Point<double> point) => Offset(point.x * scale, point.y * scale);

  @override
  void paint(Canvas canvas, Size size) {
    final glow = Paint()
      ..color = lineBlue.withValues(alpha: 0.35)
      ..strokeWidth = 6
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 4);
    final seen = Paint()
      ..color = lineBlue
      ..strokeWidth = 1.6;
    final computed = Paint()
      ..color = lineBlue.withValues(alpha: 0.45)
      ..strokeWidth = 1;
    for (final line in lines) {
      if (line.seen) {
        canvas.drawLine(onScreen(line.start), onScreen(line.end), glow);
      }
      canvas.drawLine(onScreen(line.start), onScreen(line.end), line.seen ? seen : computed);
    }
  }

  @override
  bool shouldRepaint(LinesPainter oldDelegate) => oldDelegate.lines != lines || oldDelegate.scale != scale;
}
