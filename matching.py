#Tu mają być funkcje, które dostają zdjęcia jako argumenty, tworzą im
#"dwójkąty", a potem porównują i może wyświetlają wyniki tego.

from Diangle import all_photos_diangles

#dopasowywanie zdjęć
#jest true, bo faktycznie ma działać
#na razie tylko wyświetla zdobyte diangle
def true_match_all_photos(photos):
    all_diangles = all_photos_diangles(photos)
    i=0
    try:
        for photo in all_diangles:
            print(f"PHOTO {i}:\n")
            i+=1
            for diangle in photo:
                print(diangle)
    except Exception as e:
        print(e)