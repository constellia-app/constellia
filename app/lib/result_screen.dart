import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

import 'analysis.dart';
import 'annotated_photo.dart';
import 'style.dart';

class ResultScreen extends StatelessWidget {
  final Uint8List photo;
  final Analysis? analysis;
  final VoidCallback back;
  final VoidCallback newPhoto;

  const ResultScreen(
      {super.key, required this.photo, required this.analysis, required this.back, required this.newPhoto});

  @override
  Widget build(BuildContext context) {
    final analysis = this.analysis;
    return Column(
      children: [
        Row(
          children: [
            IconButton(onPressed: back, icon: const Icon(Icons.arrow_back)),
            Expanded(child: Center(child: whiteLogo(22))),
            const SizedBox(width: 48),
          ],
        ),
        Expanded(
          child: ListView(
            padding: const EdgeInsets.symmetric(horizontal: 12),
            children: [
              ClipRRect(
                borderRadius: BorderRadius.circular(20),
                child: analysis == null ? Image.memory(photo) : AnnotatedPhoto(analysis),
              ),
              const SizedBox(height: 16),
              FilledButton.icon(
                onPressed: newPhoto,
                icon: const Icon(Icons.photo_library_outlined),
                label: const Text('Nouvelle photo'),
              ),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ],
    );
  }
}
