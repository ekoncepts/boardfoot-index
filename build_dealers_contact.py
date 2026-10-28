"""Writes dealers_contact.csv: PUBLIC contact info for every dealer, copied from each dealer's own website
(contact/about/footer pages, checked 2026-10-28). Never put anything from private email or the Vault here.
Blank field = not published on the dealer's site. Re-run after editing the DATA list; build_pages.py reads the CSV."""
import csv
COLS=['dealer','website','street','city','state','zip','phone','toll_free','fax','email','hours','contact_source_url','date_checked','note']
D='2026-10-28'
DATA=[
# dealer, website, street, city, st, zip, phone, toll_free, fax, email, hours, source, note
('Woodworkers Source','https://www.woodworkerssource.com/','18115 N. Black Canyon Hwy','Phoenix','AZ','85023','602-504-1931','800-423-2450','','nphx@woodworkerssource.com','Stores: Mon–Sat 8:00 am–5:00 pm','https://www.woodworkerssource.com/','Also has stores in Tempe (645 W. Elliot Rd, 480-355-5090) and Tucson (3441 S. Palo Verde, 520-745-8301). Toll-free line is online order help.'),
('SoCalTrim','https://socaltrim.com/','24335 Prielipp Rd #123','Wildomar','CA','92595','951-412-4175','','','store@socaltrim.com','Mon–Fri 7 am–4 pm','https://socaltrim.com/contact/',''),
('Urban Forest Mill','https://urbanforestmill.com/','33 S. Pratt Pkwy, Suite 100','Longmont','CO','80501','720-213-8405','','','tom@urbanforestmill.com','Mon–Fri 1:00–5:30 pm; Sat 10 am–4 pm','https://urbanforestmill.com/contact/','Call or text.'),
('Intercity Lumber Co.','https://www.intercitylumber.com/','5301 Causeway Blvd','Tampa','FL','33619','813-626-5232','','','','Mon–Fri 7:30 am–5:00 pm; Sat 8:00 am–4:00 pm','https://www.intercitylumber.com/',''),
('Odd Wood Lumber','https://www.owlumber.com/','8434 Afton Ln, Unit B','Port Richey','FL','34668','727-236-7198','','','info@oddwoodlumber.com','Mon–Sat 9 am–5 pm','https://www.owlumber.com/contact',''),
('The Wood Yard','https://www.thewoodyard.com/','122 Main Street','Concord','GA','30206','770-468-8588','','','store@thewoodyard.com','Mon–Fri 8 am–5 pm; Sat 8 am–12 pm','https://www.thewoodyard.com/contact-us/',''),
('Dunham Hardwoods','https://www.dunham-hardwoods.com/','3385 130th Street','Dunlap','IA','51529','712-643-5320','','712-643-2142','hardwood@iowatelecom.net','Mon–Fri 8–12 and 1–5; Sat 8–11:30','https://www.dunham-hardwoods.com/',''),
('Kunz Carpentry Warehouse','http://www.kunzcarpentry.com/','18 South Main Street','Trenton','IL','62293','618-224-9636','','','kunzcarpentry@ezeeweb.com','','https://kunzcarpentry.com/contact1.html',''),
('Detwiler Hardwood Lumber','https://detwilerhardwoodlumber.com/','2659 Shelby Street','Indianapolis','IN','46203','317-619-6756','','','detwilercustomwoodworking@gmail.com','Mon & Thu 8:00 am–5:30 pm; other days by appointment (call ahead)','https://detwilerhardwoodlumber.com/',''),
('Berkshire Products','https://berkshireproducts.com/','884 Ashley Falls Rd.','Sheffield','MA','01257','413-229-7919','','','','Mon–Fri 8:00–4:30; Sat 8:00–1:00','https://berkshireproducts.com/',''),
('Exotic Lumber','https://exoticlumber.com/','1610 Whitehall Road','Annapolis','MD','21409','410-349-1705','','','annapolis@exoticlumber.com','Mon–Fri 8:00 am–4:30 pm; Sat 9:00 am–1:00 pm','https://exoticlumber.com/pages/contact-us',''),
('Frederick Lumber Company','https://fredericklumber.com/','295 Bucheimer Rd, Suite C','Frederick','MD','21701','301-695-1271','','','info@fredericklumber.com','Mon–Fri 8:00–4:30; Sat 9–1; Sun closed','https://fredericklumber.com/',''),
('Hickory & Oak Lumber','https://hickoryandoak.com/','90931 52nd Street','Decatur','MI','49045','269-436-0039','','','hickoryandoak@gmail.com','','https://hickoryandoak.com/contact.php',''),
('Wolverine Hardwoods','https://wolverinehardwoods.com/','2810 113th Ave','Allegan','MI','49010','269-213-5887','','269-686-7944','paul@wolverinehardwoods.com','Retail: Mon–Fri 8 am–4:30 pm; Sat 8 am–noon','https://wolverinehardwoods.com/contact/','Phone shown is the retail outlet; office is 269-686-7004.'),
('Steve Wall Lumber Co.','https://walllumber.com/','7800 NC Hwy 135','Mayodan','NC','27027','336-427-0637','800-633-4062','336-427-7588','woodsales@walllumber.com','Mon–Fri 8:30–5:00; Sat 8:30–12:00','https://walllumber.com/',''),
('The Hardwood Store of NC','https://hardwoodstore.com/','100 Railroad Ave.','Gibsonville','NC','27249','336-449-9627','','','info@hardwoodstore.com','Mon–Fri 8 am–4 pm; Sat 8 am–noon','https://hardwoodstore.com/contact-us/','Second store: 175 Lane Parkway, Salisbury, NC 28146.'),
('Highland Hardwoods','https://highlandhardwoods.com/','407 Route 125','Brentwood','NH','','603-679-1230','','603-679-1960','sales@highlandhardwoods.com','Mon–Fri 8:00–4:00','https://highlandhardwoods.com/pages/contact',''),
('Willard Brothers Woodcutters','https://www.willardbrothers.net/','300 Basin Road','Trenton','NJ','08619','609-890-1990','','','info@willardbrothers.net','Mon–Fri 9 am–5 pm; Sat 9 am–3 pm','https://www.willardbrothers.net/contact',''),
('Baird Brothers Sawmill','https://www.bairdbrothers.com/','7060 Crory Rd.','Canfield','OH','44406','330-533-3122','800-732-1697','330-533-0781','','Mon–Fri 7:30 am–4 pm; Sat 7:30 am–noon (Eastern)','https://www.bairdbrothers.com/contactus.aspx',''),
('CR Muterspaw Lumber','https://crlumber.com/','3039 US-68 South','Xenia','OH','45385','937-572-9663','','','sales@crlumber.com','Mon 9–7; Tue–Fri 9–5; Sat 9–3','https://crlumber.com/contact/',''),
('KenCraft Company','https://www.kencraftcompany.com/','821 N. Westwood Ave.','Toledo','OH','43607','419-536-0333','','419-536-0944','hardwoods@kencraftcompany.com','Mon–Fri 8:30 am–5:30 pm; Sat 9 am–1 pm','https://www.kencraftcompany.com/contact/',''),
('Peacock Lumber','https://peacocklumber.ca/','328 Ritson Road North','Oshawa','ON','L1G 5P8','905-725-4744','','','','Mon–Fri 7:30 am–5 pm; Sat 8 am–4 pm','https://peacocklumber.ca/contact/',''),
('The Knotty Lumber Co. (affiliate)','https://theknottylumberco.ca/','424 Rennie Street','Hamilton','ON','L8H 3P5','905-872-4528','','','theknottylumberco@gmail.com','Tue–Fri 9:30–5:00','https://theknottylumberco.ca/pages/contact',''),
('Goby Walnut Products','https://gobywalnut.com/','25420 S. Hwy 99E','Aurora','OR','97002','503-477-6744','','503-477-6747','aaron@gobywalnut.com','Mon–Fri 8 am–4 pm; Sat 9 am–4 pm','https://gobywalnut.com/pages/contacts-location-and-hours',''),
('Hearne Hardwoods (FAS grade)','https://www.hearnehardwoods.com/','200 Whiteside Drive','Oxford','PA','19363','610-932-7400','888-814-0007','','info@hearnehardwoods.com','Mon–Fri 8 am–5 pm; Sat 8 am–4 pm','https://www.hearnehardwoods.com/',''),
('M2 Lumber','https://m2lumber.com/','110 Brickhouse Rd','Laurens','SC','29360','864-468-9663','','','info@m2lumber.com','Mon–Fri 9–5; Sat 8–3','https://m2lumber.com/pages/contact','Phone is also listed as 1-864-GOT-WOOD.'),
('The Wood Shed','https://thewoodshedtexas.com/','901 W Harris Rd, Suite 195','Arlington','TX','76001','214-399-9066','','','info@thewoodshedtexas.com','Mon–Fri 9–5; Sat 9–3','https://thewoodshedtexas.com/contact',''),
('C.P. Johnson Lumber','https://cpjohnsonlumber.com/','21457 Business Court','Elkwood','VA','22718','540-825-1006','','','info@cpjohnsonlumber.com','Mon–Fri 8:00 am–4:30 pm; Sat 8:30 am–4:30 pm','https://cpjohnsonlumber.com/',''),
('Cygnus Lumber','https://cygnuslumber.com/','','Virginia Beach','VA','','757-695-8887','','','horvathgs123@gmail.com','Mon–Fri 10 am–5 pm (contractors 8 am–5 pm); Sat 9 am–4 pm','https://cygnuslumber.com/contact-us/','No street address is published on the site; the map link searches by name.'),
('Wood Vendors (100-249 BF tier)','https://woodvendors.com/','','Vancouver','WA','','','877-983-6367','','','Mon–Fri 8:00 am–4:00 pm','https://woodvendors.com/contact-us/','No street address or general email is published; the contact page lists individual sales staff.'),
('Kettle Moraine Hardwoods','https://www.kmhardwoods.com/','5261 Aurora Road','Hartford','WI','53027','262-644-8119','','','info@kmhardwoods.com','Mon & Wed 8 am–7 pm; Tue, Thu, Fri 8 am–5 pm; Sat 8 am–3 pm','https://www.kmhardwoods.com/contact',''),
]
assert all(len(r)==13 for r in DATA)
with open('dealers_contact.csv','w',newline='') as f:
  w=csv.writer(f);w.writerow(COLS)
  for r in DATA:w.writerow(list(r[:11])+[r[11],D,r[12]])
seed={r['dealer'] for r in csv.DictReader(open('seed.csv'))}
names={r[0] for r in DATA}
print('missing from contact data:',sorted(seed-names-{d for d in seed if not d}),'| extra:',sorted(names-seed))
