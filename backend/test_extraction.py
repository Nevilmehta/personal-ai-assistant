from app.services.article_extractor import extract_article_text

def main():
    direct_article_url = input("Paste a direct publisher article URL: ").strip()

    content, final_url = extract_article_text(direct_article_url)

    print("\nResolved URL:")
    print(final_url)

    print("\nContent extracted:")
    print(bool(content))

    if content:
        print("\nExtracted preview:")
        print(content[:1000])
    else:
        print("\nNo article content was extracted.")


if __name__ == "__main__":
    main()