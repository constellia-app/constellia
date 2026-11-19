import 'package:flutter/material.dart';

import 'analysis.dart';
import 'constellation_names.dart';
import 'star_card.dart';
import 'style.dart';

class PhotoStars extends StatelessWidget {
  final Analysis analysis;

  const PhotoStars(this.analysis, {super.key});

  @override
  Widget build(BuildContext context) {
    final stars = [...analysis.stars, ...analysis.computed]..sort((a, b) => a.magnitude.compareTo(b.magnitude));
    return Padding(
      padding: const EdgeInsets.only(top: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Padding(
            padding: EdgeInsets.fromLTRB(8, 4, 8, 12),
            child: Text('Étoiles de la photo', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600)),
          ),
          InfoTable(
            titles: const ['Étoile', 'Constellation', 'Magnitude'],
            rows: [
              for (final star in stars) [star.name, frenchName(star.constellation), formatMagnitude(star.magnitude)],
            ],
            pale: [for (final star in stars) analysis.computed.contains(star)],
            onRowTap: (i) => openStarCard(context, stars[i], seen: analysis.stars.contains(stars[i])),
          ),
          const Padding(
            padding: EdgeInsets.fromLTRB(8, 8, 8, 0),
            child: Text('En gris, les étoiles non repérées sur ta photo, dont la position est calculée.',
                style: TextStyle(color: softText, fontSize: 12)),
          ),
        ],
      ),
    );
  }
}
