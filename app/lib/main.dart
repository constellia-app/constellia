import 'package:flutter/material.dart';

import 'home_screen.dart';
import 'style.dart';

void main() {
  runApp(MaterialApp(
    title: 'Constellia',
    theme: theme,
    debugShowCheckedModeBanner: false,
    home: Scaffold(
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: maxWidth),
            child: const HomeScreen(pickPhoto: null, showExample: null),
          ),
        ),
      ),
    ),
  ));
}
