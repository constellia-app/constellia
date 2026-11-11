import 'dart:math';
import 'dart:typed_data';
import 'dart:ui';

const examplePhoto = 'assets/example/photo.jpg';
const exampleAnalysis = 'assets/example/analysis.json';

class NamedStar {
  final Point<double> position;
  final int hip;

  const NamedStar(this.position, this.hip);
}

class ConstellationLine {
  final Point<double> start;
  final Point<double> end;
  final bool seen;

  const ConstellationLine(this.start, this.end, this.seen);
}

class FoundConstellation {
  final String name;
  final double confidence;
  final Rect box;

  const FoundConstellation(this.name, this.confidence, this.box);
}

class Analysis {
  final Uint8List photo;
  final int width;
  final int height;
  final List<FoundConstellation> constellations;
  final Set<String> confirmed;
  final List<NamedStar> stars;
  final List<NamedStar> computed;
  final List<ConstellationLine> lines;

  const Analysis(this.photo, this.width, this.height, this.constellations, this.confirmed,
      this.stars, this.computed, this.lines);

  factory Analysis.fromJson(Map<String, dynamic> json, Uint8List photo) {
    Point<double> point(num x, num y) => Point(x.toDouble(), y.toDouble());
    NamedStar star(List values) => NamedStar(point(values[0], values[1]), values[2] as int);
    Rect box(List values) => Rect.fromLTRB((values[0] as num).toDouble(), (values[1] as num).toDouble(),
        (values[2] as num).toDouble(), (values[3] as num).toDouble());

    return Analysis(
      photo,
      json['width'] as int,
      json['height'] as int,
      [
        for (final c in json['constellations'] as List)
          FoundConstellation(c['name'] as String, (c['confidence'] as num).toDouble(), box(c['box'] as List)),
      ],
      {for (final name in json['confirmed'] as List) name as String},
      [for (final s in json['stars'] as List) star(s as List)],
      [for (final s in json['computed'] as List) star(s as List)],
      [
        for (final l in json['lines'] as List)
          ConstellationLine(point(l[0], l[1]), point(l[2], l[3]), l[4] as bool),
      ],
    );
  }
}
