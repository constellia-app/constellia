import 'package:flutter/material.dart';

const darkBlue = Color(0xFF070B1A);
const cardBlue = Color(0xFF111A33);
const lineBlue = Color(0xFF9CCBFF);
const softText = Color(0xFFB8C2D9);

const logo = 'assets/images/logo.png';
const banner = 'assets/images/banniere.png';

const maxWidth = 480.0;

final theme = ThemeData(
  brightness: Brightness.dark,
  scaffoldBackgroundColor: darkBlue,
  colorScheme: const ColorScheme.dark(primary: lineBlue, surface: cardBlue),
  filledButtonTheme: FilledButtonThemeData(
    style: FilledButton.styleFrom(
      backgroundColor: Colors.white,
      foregroundColor: darkBlue,
      minimumSize: const Size.fromHeight(52),
      textStyle: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
    ),
  ),
  outlinedButtonTheme: OutlinedButtonThemeData(
    style: OutlinedButton.styleFrom(
      foregroundColor: Colors.white,
      minimumSize: const Size.fromHeight(52),
      side: const BorderSide(color: Colors.white54),
      textStyle: const TextStyle(fontSize: 16),
    ),
  ),
);

Widget whiteLogo(double height) {
  return Image.asset(logo, height: height, color: Colors.white, colorBlendMode: BlendMode.srcIn);
}
