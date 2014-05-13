module IRCDB.Parser where

import Control.Applicative((<*>), (<$>), (*>), (<*))
import Text.Parsec
import Text.Parsec.String
import qualified Text.Parsec.Token as P
import Text.Parsec.Language (emptyDef)
import Data.Functor.Identity
import Data.Time.LocalTime
import IRCDB.Time

type Name = String
type Contents = String



data DataLine = Message Time Int Name Contents
              | Status Time String
              | Nick Time Name Name
              | Notice Time String
              | Invite Time String
              | Day LocalTime
              | Close LocalTime
              | Open LocalTime
    deriving (Show)

data Log = Log [DataLine] deriving (Show)

logLength :: Log -> Int
logLength (Log ls) = length ls

lexer :: P.GenTokenParser String a Identity
lexer = P.makeTokenParser $ emptyDef

integer :: Parser Integer
integer = P.integer lexer

whiteSpace :: Parser ()
whiteSpace = P.whiteSpace lexer

lexeme :: Parser String -> Parser String
lexeme = P.lexeme lexer

identifier :: Parser String
identifier = P.identifier lexer

symbol :: String -> Parser String
symbol = P.symbol lexer

parseDataLine :: Parser DataLine
parseDataLine = try (parseTimeChange) <|> parseChatLine

parseChatLine :: Parser DataLine
parseChatLine = try parseStatus
            <|> try parseNotice
            <|> try parseAction
            <|> try parseInvite
            <|> parseMessage


parseTimeChange :: Parser DataLine
parseTimeChange = try (Day <$> (symbol "--- Day changed" *> parseDateString))
              <|> try (Close <$> (symbol "--- Log closed" *> parseDateString))
              <|> (Open <$> (symbol "--- Log opened" *> parseDateString))

parseInvite :: Parser DataLine
parseInvite = Invite <$> parseTime
                     <*> ((symbol "!") *> eatLine)

parseNotice :: Parser DataLine
parseNotice = Notice <$> parseTime
                     <*> ((symbol "-") *> eatLine)

parseStatus :: Parser DataLine
parseStatus = try parseNickChange <|> parseGenStatus

parseGenStatus :: Parser DataLine
parseGenStatus = Status <$> parseTime
                        <*> (symbol "-!-" *> eatLine)

parseNick :: Parser Name
parseNick = many (noneOf " ") <* whiteSpace

parseNickChange :: Parser DataLine
parseNickChange = Nick <$> parseTime
                       <*> (symbol "-!-" *> parseNick)
                       <*> (symbol "is now known as" *> parseNick)


parseAction :: Parser DataLine
parseAction = Message <$> parseTime
                      <*> return 1
                      <*> (symbol "*" *> parseNick)
                      <*> eatLine

parseMessage :: Parser DataLine
parseMessage = Message <$> parseTime
                       <*> return 0
                       <*> (string "<" *> oneOf " +~@%&" *> parseName <* symbol ">")
                       <*> parseContents

parseInt :: Parser Int
parseInt = fromInteger <$> integer

parseTime :: Parser Time
parseTime = (,) <$> (parseInt <* symbol ":")
                <*> parseInt

parseName :: Parser Name
parseName = manyTill anyChar (lookAhead (symbol ">"))

eatLine :: Parser String
eatLine = manyTill anyChar eof

parseContents :: Parser Contents
parseContents = eatLine


get :: Maybe LocalTime -> LocalTime
get = maybe (anyTime) id

parseDateString :: Parser LocalTime
parseDateString = (get . stringToLocalTime) <$> eatLine

parseLine :: (Int, String) -> Either (Int, String, String) DataLine
parseLine (ln, s) =
    case parse parseDataLine "" s of
        Left err -> Left (ln, s, show err)
        Right success -> Right success
