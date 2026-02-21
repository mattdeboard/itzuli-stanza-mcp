#!/usr/bin/env python3
"""
Interactive playground for testing the Itzuli translation API.
Reads API key from .env file and provides simple interface to test translations.
"""

import os
from dotenv import load_dotenv
from Itzuli import Itzuli

load_dotenv()


def main():
    api_key = os.environ.get("ITZULI_API_KEY", "")
    if not api_key:
        print("ERROR: ITZULI_API_KEY not found in .env file")
        return

    client = Itzuli(api_key)

    print("Itzuli API Playground")
    print("====================")
    print("Supported language pairs: eu<->es, eu<->en, eu<->fr")
    print("Commands:")
    print("  translate <text> <source> <target>  - Translate text")
    print("  quota                               - Check API quota")
    print("  quit                                - Exit")
    print()

    while True:
        try:
            command = input("> ").strip()

            if command == "quit":
                break
            elif command == "quota":
                try:
                    quota = client.getQuota()
                    print(f"Quota: {quota}")
                except Exception as e:
                    print(f"Error getting quota: {e}")
            elif command.startswith("translate "):
                # Parse: translate "text with spaces" source target
                import shlex
                try:
                    parts = shlex.split(command)
                    if len(parts) != 4:
                        print("Usage: translate \"<text>\" <source> <target>")
                        print("Example: translate \"hello my friend\" en eu")
                        continue
                    
                    _, text, source, target = parts
                except ValueError as e:
                    print(f"Parse error: {e}")
                    print("Usage: translate \"<text>\" <source> <target>")
                    continue
                try:
                    print(f"text: {text}; source: {source}; target: {target}")
                    result = client.getTranslation(text, source, target)
                    print(f"Translation: {result}")
                except Exception as e:
                    print(f"Error translating: {e}")
            else:
                print("Unknown command. Type 'quit' to exit.")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except EOFError:
            break


if __name__ == "__main__":
    main()
