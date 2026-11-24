import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

import 'analysis.dart';
import 'annotated_photo.dart';
import 'share_photo.dart';
import 'star_table.dart';
import 'style.dart';

class ResultScreen extends StatefulWidget {
  final Uint8List photo;
  final Analysis? analysis;
  final VoidCallback back;
  final VoidCallback newPhoto;

  const ResultScreen(
      {super.key, required this.photo, required this.analysis, required this.back, required this.newPhoto});

  @override
  State<ResultScreen> createState() => _ResultScreenState();
}

class _ResultScreenState extends State<ResultScreen> {
  final _photoKey = GlobalKey();
  bool _sharing = false;

  Future<void> _share(Analysis analysis) async {
    setState(() => _sharing = true);
    try {
      await shareAnnotatedPhoto(_photoKey, analysis.width);
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(const SnackBar(content: Text('Impossible de partager la photo.')));
      }
    }
    if (mounted) {
      setState(() => _sharing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final analysis = widget.analysis;
    return Column(
      children: [
        Row(
          children: [
            IconButton(onPressed: widget.back, icon: const Icon(Icons.arrow_back)),
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
                child: analysis == null
                    ? Image.memory(widget.photo)
                    : RepaintBoundary(key: _photoKey, child: AnnotatedPhoto(analysis)),
              ),
              if (analysis != null) ...[
                const SizedBox(height: 12),
                OutlinedButton.icon(
                  onPressed: _sharing ? null : () => _share(analysis),
                  icon: const Icon(Icons.share_outlined),
                  label: const Text('Partager'),
                ),
                PhotoStars(analysis),
              ],
              const SizedBox(height: 16),
              FilledButton.icon(
                onPressed: widget.newPhoto,
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
