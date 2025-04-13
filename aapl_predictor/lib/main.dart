import 'package:aapl_predictor/home.dart';
import 'package:flutter/material.dart';

void main() {
  runApp(const AAPL());
}

class AAPL extends StatelessWidget {
  const AAPL({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: Home(),
    );
  }
}
