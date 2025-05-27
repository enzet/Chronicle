" Vim syntax file
" Language: Chronicle timeline file
" Maintainer: Sergey Vartanov
" Latest Revision: 24 May 2023

" This probably crashes Vim:
" au BufRead,BufNewFile *.txt set filetype=chronicle

if exists("b:current_syntax")
   finish
endif

syntax match chronicleTime /\v(\d{4}-\d{2}-\d{2}|\d{2}:\d{2}|\d{4}-\d{2}-\d{2}T\d{2}:\d{2})(\/(\d{4}-\d{2}-\d{2}|\d{2}:\d{2}|\d{4}-\d{2}-\d{2}T\d{2}:\d{2}))?/

hi link DoArguments chronicleEventValue
syntax match DoArguments /\v![a-z0-9_]+/ contained

hi link CleanArguments chronicleEventValue
syntax match CleanArguments /\v(body|head)/ contained

hi link ShaveArguments chronicleEventValue
syntax match ShaveArguments /\v(body|face)/ contained

hi link PodcastArguments chronicleEventValue
syntax match PodcastArguments /\v\@[a-z0-9_]+/ contained

hi link ProgramArguments chronicleEventValue
syntax match ProgramArguments /\v\.[a-z]+/ contained
syntax match ProgramArguments /\v\@[a-z0-9_]+/ contained
syntax match ProgramArguments /\v![a-z0-9_]+/ contained
syntax match ProgramArguments /\v#[a-z0-9#]+/ contained

hi link Interval chronicleEventValue
syntax match Interval /\v(\d+:)?\d?\d:\d\d\/(\d+:)?\d?\d:\d\d/ contained

hi link Duration chronicleEventValue
syntax match Duration /\v(\d+:)?\d?\d:\d\d/ contained

hi link Season chronicleEventValue
syntax match Season /\vs\d+/ contained

hi link Episode chronicleEventValue
syntax match Episode /\ve\d+/ contained

hi link Language chronicleEventValue
syntax match Language /\v\.[a-z][a-z]/ contained

hi link Subtitles chronicleEventValue
syntax match Subtitles /\v_[a-z][a-z]/ contained

hi link Subject chronicleEventValue
syntax match Subject /\v(\/[a-z]+)+/ contained

hi link Tag chronicleEventValue
syntax match Tag /\v![a-z0-9_]+/ contained

hi link Blue chronicleEventValueBlue
syntax match Blue /\vblue/ contained

hi link Gray chronicleEventValueGray
syntax match Gray /\vgray/ contained

hi link Black chronicleEventValueBlack
syntax match Black /\vblack/ contained

hi link Red chronicleEventValueRed
syntax match Red /\vred/ contained

hi link Green chronicleEventValueGreen
syntax match Green /\vgreen/ contained

hi link Yellow chronicleEventValueYellow
syntax match Yellow /\vyellow/ contained

hi link DarkBlue chronicleEventValueDarkBlue
syntax match DarkBlue /\vdarkblue/ contained

hi link DarkGreen chronicleEventValueDarkGreen
syntax match DarkGreen /\vdarkgreen/ contained

hi link DarkRed chronicleEventValueDarkRed
syntax match DarkRed /\vdarkred/ contained

hi link LightBlue chronicleEventValueLightBlue
syntax match LightBlue /\vlightblue/ contained

hi link LightGreen chronicleEventValueLightGreen
syntax match LightGreen /\vlightgreen/ contained

hi link LightRed chronicleEventValueLightRed
syntax match LightRed /\vlightred/ contained

hi link Link chronicleLink
syntax match Link /\vhttps?:\/\/[^ ]+/ contained

hi Prefix guifg=gray gui=italic
syntax match Prefix /\v(using|with|at|order:|theme:|laundry:|size:|season:)/ contained

syntax match chronicleVariable /\v\@[a-z0-9_]+/ contained
syntax match chronicleTask "#[0-9a-z_!#-]\+" contains=@NoSpell

syntax region AbsLine matchgroup=TypeFormat start=/abs\s*/ end=/$/ contains=AbsArguments
syntax region AirportLine matchgroup=TypeFormat start=/airport\s*/ end=/$/ contains=AirportArguments
syntax region AppointmentLine matchgroup=TypeFormat start=/appointment\s*/ end=/$/ contains=AppointmentArguments
syntax region AudiobookLine matchgroup=TypeFormat start=/audiobook\s*/ end=/$/ contains=AudiobookArguments
syntax region BankLine matchgroup=TypeFormat start=/bank\s*/ end=/$/ contains=BankArguments
syntax region BalletLine matchgroup=TypeFormat start=/ballet\s*/ end=/$/ contains=BalletArguments
syntax region BarLine matchgroup=TypeFormat start=/bar\s*/ end=/$/ contains=BarArguments
syntax region BookLine matchgroup=TypeFormat start=/book\s*/ end=/$/ contains=BookArguments
syntax region Book_objectLine matchgroup=TypeFormat start=/book_object\s*/ end=/$/ contains=Book_objectArguments
syntax region BuyLine matchgroup=TypeFormat start=/buy\s*/ end=/$/ contains=BuyArguments
syntax region CafeLine matchgroup=TypeFormat start=/cafe\s*/ end=/$/ contains=CafeArguments
syntax region CoatLine matchgroup=TypeFormat start=/coat\s*/ end=/$/ contains=CoatArguments
syntax region JacketLine matchgroup=TypeFormat start=/jacket\s*/ end=/$/ contains=JacketArguments
syntax region CallLine matchgroup=TypeFormat start=/call\s*/ end=/$/ contains=CallArguments
syntax region CardLine matchgroup=TypeFormat start=/card\s*/ end=/$/ contains=CardArguments
syntax region Chin_upsLine matchgroup=TypeFormat start=/chin_ups\s*/ end=/$/ contains=Chin_upsArguments
syntax region CinemaLine matchgroup=TypeFormat start=/cinema\s*/ end=/$/ contains=CinemaArguments
syntax region CleanLine matchgroup=TypeFormat start=/clean\s*/ end=/$/ contains=CleanArguments,Tag,chronicleVariable
syntax region ClinicLine matchgroup=TypeFormat start=/clinic\s*/ end=/$/ contains=ClinicArguments
syntax region ClubLine matchgroup=TypeFormat start=/club\s*/ end=/$/ contains=ClubArguments
syntax region CookLine matchgroup=TypeFormat start=/cook\s*/ end=/$/ contains=CookArguments
syntax region CountryLine matchgroup=TypeFormat start=/country\s*/ end=/$/ contains=CountryArguments
syntax region CupLine matchgroup=TypeFormat start=/cup\s*/ end=/$/ contains=CupArguments
syntax region DeviceLine matchgroup=TypeFormat start=/device\s*/ end=/$/ contains=DeviceArguments
syntax region DipsLine matchgroup=TypeFormat start=/dips\s*/ end=/$/ contains=DipsArguments
syntax region DoLine matchgroup=TypeFormat start=/do\s*/ end=/$/ contains=DoArguments,chronicleVariable,chronicleComment
syntax region DrawLine matchgroup=TypeFormat start=/draw\s*/ end=/$/ contains=DrawArguments
syntax region DrinkLine matchgroup=TypeFormat start=/drink\s*/ end=/$/ contains=DrinkArguments
syntax region EatLine matchgroup=TypeFormat start=/eat\s*/ end=/$/ contains=EatArguments
syntax region GlassesLine matchgroup=TypeFormat start=/glasses\s*/ end=/$/ contains=GlassesArguments
syntax region HeadphonesLine matchgroup=TypeFormat start=/headphones\s*/ end=/$/ contains=HeadphonesArguments
syntax region High_kneeLine matchgroup=TypeFormat start=/high_knee\s*/ end=/$/ contains=High_kneeArguments
syntax region HomeLine matchgroup=TypeFormat start=/home\s*/ end=/$/ contains=HomeArguments
syntax region HotelLine matchgroup=TypeFormat start=/hotel\s*/ end=/$/ contains=HotelArguments
syntax region Jumping_jacksLine matchgroup=TypeFormat start=/jumping_jacks\s*/ end=/$/ contains=Jumping_jacksArguments
syntax region Kick_scooterLine matchgroup=TypeFormat start=/kick_scooter\s*/ end=/$/ contains=Kick_scooterArguments
syntax region LearnLine matchgroup=TypeFormat start=/learn\s*/ end=/$/ contains=LearnArguments,Subject,Duration,Prefix,chronicleVariable
syntax region LectureLine matchgroup=TypeFormat start=/lecture\s*/ end=/$/ contains=LectureArguments
syntax region ListenLine matchgroup=TypeFormat start=/listen\s*/ end=/$/ contains=ListenArguments
syntax region MetroLine matchgroup=TypeFormat start=/metro\s*/ end=/$/ contains=MetroArguments
syntax region MovieLine matchgroup=TypeFormat start=/movie\s*/ end=/$/ contains=MovieArguments
syntax region ParkLine matchgroup=TypeFormat start=/park\s*/ end=/$/ contains=ParkArguments
syntax region PayLine matchgroup=TypeFormat start=/pay\s*/ end=/$/ contains=PayArguments
syntax region PersonLine matchgroup=TypeFormat start=/person\s*/ end=/$/ contains=PersonArguments
syntax region PharmacyLine matchgroup=TypeFormat start=/pharmacy\s*/ end=/$/ contains=PharmacyArguments
syntax region PhoneLine matchgroup=TypeFormat start=/phone\s*/ end=/$/ contains=PhoneArguments
syntax region PlaneLine matchgroup=TypeFormat start=/plane\s*/ end=/$/ contains=PlaneArguments
syntax region PodcastLine matchgroup=TypeFormat start=/podcast\s*/ end=/$/ contains=Interval,Season,Episode,chronicleVariable,chronicleTask,chronicleComment
syntax region ProgramLine matchgroup=TypeFormat start=/program\s*/ end=/$/ contains=ProgramArguments,chronicleVariable,chronicleTask,chronicleComment
syntax region ProjectLine matchgroup=TypeFormat start=/project\s*/ end=/$/ contains=ProjectArguments
syntax region Push_upsLine matchgroup=TypeFormat start=/push_ups\s*/ end=/$/ contains=Push_upsArguments
syntax region ReadLine matchgroup=TypeFormat start=/read\s*/ end=/$/ contains=ReadArguments
syntax region ReviewLine matchgroup=TypeFormat start=/review\s*/ end=/$/ contains=ReviewArguments
syntax region RunLine matchgroup=TypeFormat start=/run\s*/ end=/$/ contains=RunArguments
syntax region Russian_twistsLine matchgroup=TypeFormat start=/russian_twists\s*/ end=/$/ contains=Russian_twistsArguments
syntax region ShaveLine matchgroup=TypeFormat start=/shave\s*/ end=/$/ contains=ShaveArguments
syntax region ShopLine matchgroup=TypeFormat start=/shop\s*/ end=/$/ contains=ShopArguments
syntax region ShowLine matchgroup=TypeFormat start=/show\s*/ end=/$/ contains=ShowArguments
syntax region SleepLine matchgroup=TypeFormat start=/sleep\s*/ end=/$/ contains=SleepArguments
syntax region SquatsLine matchgroup=TypeFormat start=/squats\s*/ end=/$/ contains=SquatsArguments
syntax region StationLine matchgroup=TypeFormat start=/station\s*/ end=/$/ contains=StationArguments
syntax region TaxiLine matchgroup=TypeFormat start=/taxi\s*/ end=/$/ contains=TaxiArguments,chronicleVariable
syntax region UniversityLine matchgroup=TypeFormat start=/university\s*/ end=/$/ contains=UniversityArguments
syntax region WalkLine matchgroup=TypeFormat start=/walk\s*/ end=/$/ contains=WalkArguments
syntax region Warm_upLine matchgroup=TypeFormat start=/warm_up\s*/ end=/$/ contains=Warm_upArguments
syntax region WriteLine matchgroup=TypeFormat start=/write\s*/ end=/$/ contains=WriteArguments,chronicleVariable,Tag,Prefix
syntax region WatchLine matchgroup=TypeFormat start=/watch\s*/ end=/$/ contains=Language,Subtitles,Season,Episode,Interval,Duration,chronicleVariable

syntax region ComputerLine matchgroup=TypeFormat start=/computer\s*/ end=/$/ contains=ComputerArguments,chronicleVariable,Link,Cost,Red,Green,Blue,LightRed,LightGreen,LightBlue,DarkRed,DarkGreen,DarkBlue,Gray,Black,Yellow
syntax region MedicationLine matchgroup=TypeFormat start=/medication\s*/ end=/$/ contains=MedicationArguments,chronicleVariable,Link,Cost,Red,Green,Blue,LightRed,LightGreen,LightBlue,DarkRed,DarkGreen,DarkBlue,Gray,Black,Yellow
syntax region PackLine matchgroup=TypeFormat start=/pack\s*/ end=/$/ contains=PackArguments,chronicleVariable,Link,Cost,Red,Green,Blue,LightRed,LightGreen,LightBlue,DarkRed,DarkGreen,DarkBlue,Gray,Black,Yellow
syntax region ShoesLine matchgroup=TypeFormat start=/shoes\s*/ end=/$/ contains=ShoesArguments,chronicleVariable,Link,Cost,Red,Green,Blue,LightRed,LightGreen,LightBlue,DarkRed,DarkGreen,DarkBlue,Gray,Black,Yellow
syntax region SocksLine matchgroup=TypeFormat start=/socks\s*/ end=/$/ contains=SocksArguments,chronicleVariable,Link,Cost,Red,Green,Blue,LightRed,LightGreen,LightBlue,DarkRed,DarkGreen,DarkBlue,Gray,Black,Yellow
syntax region ThingLine matchgroup=TypeFormat start=/thing\s*/ end=/$/ contains=ThingArguments,chronicleVariable,Link,Cost,Red,Green,Blue,LightRed,LightGreen,LightBlue,DarkRed,DarkGreen,DarkBlue,Gray,Black,Yellow
syntax region SweaterLine matchgroup=TypeFormat start=/sweater\s*/ end=/$/ contains=SweaterArguments,chronicleVariable,Link,Cost,Red,Green,Blue,LightRed,LightGreen,LightBlue,DarkRed,DarkGreen,DarkBlue,Gray,Black,Yellow
syntax region PantsLine matchgroup=TypeFormat start=/pants\s*/ end=/$/ contains=PantsArguments,Prefix,chronicleVariable,Link,Cost,Red,Green,Blue,LightRed,LightGreen,LightBlue,DarkRed,DarkGreen,DarkBlue,Gray,Black,Yellow
syntax region UnderpantsLine matchgroup=TypeFormat start=/underpants\s*/ end=/$/ contains=UnderpantsArguments,chronicleVariable,Link,Cost,Red,Green,Blue,LightRed,LightGreen,LightBlue,DarkRed,DarkGreen,DarkBlue,Gray,Black,Yellow
syntax region T_shirtLine matchgroup=TypeFormat start=/t_shirt\s*/ end=/$/ contains=T_shirtArguments,chronicleVariable,Link,Cost,Red,Green,Blue,LightRed,LightGreen,LightBlue,DarkRed,DarkGreen,DarkBlue,Gray,Black,Yellow

hi link TypeFormat chronicleEventType

" Warnings.

syntax match chronicleCurrent ">>>"
syntax match chronicleTaskPromise "<\.>"
syntax match chronicleTaskImportant "<!>"
syntax match chronicleTaskThisDay "<\*>"

syntax match chronicleDate "^\s*\d\d\d\d-\d\d-\d\d$"
syntax match chronicleComment "-- .*"
syntax match chronicleTaskMarkerDo "\[ \]"
syntax match chronicleTaskMarkerDone "\[[x×-]\]"
syntax match chronicleTaskMarkerNotDone "\[/\]"
