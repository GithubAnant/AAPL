import 'package:aapl_predictor/calender.dart';
import 'package:flutter/material.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';

class Home extends StatefulWidget {
  const Home({super.key});

  @override
  State<Home> createState() => _HomeState();
}

class _HomeState extends State<Home> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBodyBehindAppBar: true,
      appBar: AppBar(
        leading: Center(child: FaIcon(FontAwesomeIcons.apple, color: Colors.white)),
        title: Text('AAPL', style: TextStyle(color: Colors.white, fontFamily: 'Montserrat'),),
        backgroundColor: const Color.fromARGB(178, 0, 0, 0),
      ),
      body: StackLander(),
    );
  }
}

class StackLander extends StatelessWidget {
  const StackLander({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        Positioned.fill(
          child: Image.asset('assets/images/backdrop.jpg', fit: BoxFit.cover),
        ),
        Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // HERO TEXT
              Text(
                'Predict AAPL Stock Price',
                style: TextStyle(
                  color: Colors.white,
                  fontFamily: 'Montserrat',
                  fontSize: MediaQuery.of(context).size.width * 0.033,
                  fontWeight: FontWeight.w600,
                ),
              ),

              // gap
              SizedBox(height: MediaQuery.of(context).size.height * 0.012),

              ElevatedButton(onPressed: (){
                Navigator.push(context, MaterialPageRoute(builder: (context) => CalendarPage()));
              }, 
              style: ElevatedButton.styleFrom(
                elevation: 5,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(10)
                )
              ),
              child: Padding(
                
                padding: const EdgeInsets.all(8.0),
                child: Text('Choose a Date', style: TextStyle(color: Colors.black, fontFamily: 'Montserrat', fontSize: 20),),
              )),

              // gap
              SizedBox(height: MediaQuery.of(context).size.height * 0.019),

            ],
          ),
        ),

      ],
    );
  }
}
