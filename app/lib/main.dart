import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:image_picker/image_picker.dart';

import 'analysis.dart';
import 'home_screen.dart';
import 'result_screen.dart';
import 'style.dart';

void main() {
  runApp(MaterialApp(
    title: 'Constellia',
    theme: theme,
    debugShowCheckedModeBanner: false,
    home: const ConstelliaApp(),
  ));
}

class ConstelliaApp extends StatefulWidget {
  const ConstelliaApp({super.key});

  @override
  State<ConstelliaApp> createState() => _ConstelliaAppState();
}

class _ConstelliaAppState extends State<ConstelliaApp> {
  Uint8List? _photo;
  Analysis? _analysis;

  Future<void> _pickPhoto() async {
    final picked = await ImagePicker().pickImage(source: ImageSource.gallery);
    if (picked == null) {
      return;
    }
    final photo = await picked.readAsBytes();
    setState(() {
      _photo = photo;
      _analysis = null;
    });
  }

  Future<void> _showExample() async {
    final photo = (await rootBundle.load(examplePhoto)).buffer.asUint8List();
    final json = jsonDecode(await rootBundle.loadString(exampleAnalysis)) as Map<String, dynamic>;
    setState(() {
      _photo = photo;
      _analysis = Analysis.fromJson(json, photo);
    });
  }

  @override
  Widget build(BuildContext context) {
    final photo = _photo;
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: maxWidth),
            child: photo == null
                ? HomeScreen(pickPhoto: _pickPhoto, showExample: _showExample)
                : ResultScreen(
                    photo: photo,
                    analysis: _analysis,
                    back: () => setState(() => _photo = null),
                    newPhoto: _pickPhoto,
                  ),
          ),
        ),
      ),
    );
  }
}
