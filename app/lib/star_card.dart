import 'package:flutter/material.dart';

import 'analysis.dart';
import 'constellation_names.dart';
import 'style.dart';

void openStarCard(BuildContext context, NamedStar star, {required bool seen}) {
  showModalBottomSheet(
    context: context,
    backgroundColor: cardBlue,
    isScrollControlled: true,
    builder: (_) => StarCard(star, seen),
  );
}

String formatMagnitude(double magnitude) => magnitude.toStringAsFixed(2).replaceAll('.', ',');

class StarCard extends StatelessWidget {
  final NamedStar star;
  final bool seen;

  const StarCard(this.star, this.seen, {super.key});

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(frenchName(star.constellation).toUpperCase(),
                style: constellationNameStyle.copyWith(color: lineBlue, shadows: [])),
            const SizedBox(height: 6),
            Text(star.name, style: const TextStyle(fontSize: 30, fontWeight: FontWeight.w600)),
            const SizedBox(height: 20),
            InfoTable(
              titles: const ['Magnitude', 'Hipparcos'],
              rows: [
                [formatMagnitude(star.magnitude), '${star.hip}'],
              ],
            ),
            if (!seen)
              const Padding(
                padding: EdgeInsets.only(top: 12),
                child: Text(
                  'Non repérée sur ta photo, sa position est calculée.',
                  style: TextStyle(color: softText, fontStyle: FontStyle.italic),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class InfoTable extends StatelessWidget {
  final List<String> titles;
  final List<List<String>> rows;
  final List<bool>? pale;
  final void Function(int row)? onRowTap;

  const InfoTable({super.key, required this.titles, required this.rows, this.pale, this.onRowTap});

  @override
  Widget build(BuildContext context) {
    return Table(
      border: TableBorder.all(color: Colors.white24, borderRadius: BorderRadius.circular(12)),
      defaultVerticalAlignment: TableCellVerticalAlignment.middle,
      children: [
        TableRow(
          decoration: const BoxDecoration(color: darkBlue),
          children: [
            for (final title in titles) TableText(title, style: const TextStyle(color: softText, fontSize: 13)),
          ],
        ),
        for (var i = 0; i < rows.length; i++)
          TableRow(children: [
            for (final value in rows[i])
              TableRowInkWell(
                onTap: onRowTap == null ? null : () => onRowTap!(i),
                child: TableText(value, style: TextStyle(color: (pale?[i] ?? false) ? softText : Colors.white)),
              ),
          ]),
      ],
    );
  }
}

class TableText extends StatelessWidget {
  final String text;
  final TextStyle? style;

  const TableText(this.text, {super.key, this.style});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
      child: Text(text, style: style),
    );
  }
}
