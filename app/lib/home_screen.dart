import 'package:flutter/material.dart';

import 'style.dart';

const bannerRatio = 0.8;
const bannerAlignment = Alignment(-0.61, 0);

class HomeScreen extends StatelessWidget {
  final VoidCallback? pickPhoto;
  final VoidCallback? showExample;

  const HomeScreen({super.key, required this.pickPhoto, required this.showExample});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Expanded(child: Align(alignment: Alignment.bottomCenter, child: bannerImage())),
        Padding(
          padding: const EdgeInsets.fromLTRB(28, 8, 28, 36),
          child: Column(
            children: [
              whiteLogo(44),
              const SizedBox(height: 12),
              const Text(
                'Reconnaît les constellations sur une photo du ciel et donne le nom de chaque étoile.',
                textAlign: TextAlign.center,
                style: TextStyle(color: softText, fontSize: 15, height: 1.4),
              ),
              const SizedBox(height: 32),
              FilledButton.icon(
                onPressed: pickPhoto,
                icon: const Icon(Icons.photo_library_outlined),
                label: const Text('Choisir une photo'),
              ),
              const SizedBox(height: 12),
              OutlinedButton(onPressed: showExample, child: const Text('Voir un exemple')),
            ],
          ),
        ),
      ],
    );
  }

  Widget bannerImage() {
    return AspectRatio(
      aspectRatio: bannerRatio,
      child: Stack(
        fit: StackFit.expand,
        children: [
          Image.asset(banner, fit: BoxFit.cover, alignment: bannerAlignment),
          const DecoratedBox(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [darkBlue, Colors.transparent, Colors.transparent, darkBlue],
                stops: [0, 0.15, 0.6, 1],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
